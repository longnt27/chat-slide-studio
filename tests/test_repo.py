"""Regressions: schema, image integrity and documentation contract.

These tests do not need network or GitHub secrets.
"""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from check_spec import validate
from fit_image import fit_image
from new_deck import new_deck
from check_storyboard import (validate_plan, validate_approval, check_deck_against_plan,
    approve, digest, reveal_sequence)
from patch_animations import patch
from zipfile import ZipFile
from lxml import etree
from pptx import Presentation
from PIL import Image

class RepoTests(unittest.TestCase):
    def test_demo_schema_ok(self):
        info=validate(ROOT/'decks/demo/deck.json')
        self.assertEqual(info['slides'],15)
        self.assertEqual(info['requested_slide_count'],15)
        self.assertEqual(info['morphs'],[3])

    def test_slide_count_fewer_than_requested_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            deck=deepcopy(json.loads((ROOT/'decks/demo/deck.json').read_text()))
            deck['slides']=deck['slides'][:8]
            (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False))
            (folder/'sources.json').write_text((ROOT/'decks/demo/sources.json').read_text())
            with self.assertRaisesRegex(ValueError,'slide_count_mismatch: user requested 15, spec contains 8'):
                validate(folder/'deck.json')

    def test_slide_count_more_than_requested_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            deck=deepcopy(json.loads((ROOT/'decks/demo/deck.json').read_text()))
            deck['slides'].insert(-1,deepcopy(deck['slides'][7]))
            (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False))
            (folder/'sources.json').write_text((ROOT/'decks/demo/sources.json').read_text())
            with self.assertRaisesRegex(ValueError,'slide_count_mismatch: user requested 15, spec contains 16'):
                validate(folder/'deck.json')

    def test_requested_slide_count_mandatory(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            deck=deepcopy(json.loads((ROOT/'decks/demo/deck.json').read_text()))
            del deck['requested_slide_count']
            (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False))
            (folder/'sources.json').write_text((ROOT/'decks/demo/sources.json').read_text())
            with self.assertRaisesRegex(ValueError, 'requested_slide_count'):
                validate(folder/'deck.json')

    def test_morph_wrong_subject_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            deck=deepcopy(json.loads((ROOT/'decks/demo/deck.json').read_text()))
            sources=json.loads((ROOT/'decks/demo/sources.json').read_text())
            (folder/'sources.json').write_text(json.dumps(sources))
            deck['slides'][2]['morph_id']='different_subject'
            (folder/'deck.json').write_text(json.dumps(deck))
            with self.assertRaisesRegex(ValueError,'Morph needs same image asset'):
                validate(folder/'deck.json')

    def test_cropping_subject_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            original=p/'portrait.png'
            Image.new('RGB',(300,500),(240,188,129)).save(original)
            with self.assertRaisesRegex(ValueError,'Cover cropping forbidden'):
                fit_image(original,p/'out.jpg',800,400,mode='cover')
            result=fit_image(original,p/'safe.jpg',800,400,mode='contain')
            self.assertTrue((p/'safe.jpg').exists())
            self.assertGreater(result['aspect_mismatch'],1.0)

    def test_new_deck_scaffold_matches_user_count(self):
        for slides in (1,12,15,20):
            with self.subTest(slides=slides), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                (root/'decks').mkdir()
                new_deck('count-test','Test of presentation length',slides=slides,root=root)
                folder=root/'decks/count-test'
                self.assertFalse((folder/'deck.json').exists(), 'Do not build before HITL approval')
                spec=json.loads((folder/'storyboard.json').read_text())
                self.assertEqual(spec['requested_slide_count'],slides)
                self.assertEqual(len(spec['slides']),slides)
                if slides>1:
                    self.assertEqual(spec['slides'][-1]['layout'],'thanks')

    def test_unfilled_skeleton_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'decks').mkdir()
            new_deck('count-test','Test of presentation length',slides=15,root=root)
            with self.assertRaisesRegex(ValueError,'TODO placeholders'):
                validate_plan(root/'decks/count-test')

    def test_hitl_lock_required_and_stale_plan_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'human-test'
            folder.mkdir()
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            deck=json.loads((ROOT/'decks/demo/deck.json').read_text())
            plan['deck_id']='human-test'
            deck['id']='human-test'
            (folder/'storyboard.json').write_text(json.dumps(plan))
            (folder/'deck.json').write_text(json.dumps(deck))
            self.assertEqual(len(validate_plan(folder)['slides']),15)
            with self.assertRaisesRegex(ValueError,'approval missing'):
                validate_approval(folder)
            self.assertFalse((folder/'approval.json').exists())
            locked=approve(folder,'Tôi duyệt bố cục 15 slide trong storyboard này')
            self.assertEqual(locked['storyboard_sha256'],digest(plan))
            self.assertTrue(check_deck_against_plan(folder))
            plan['slides'][1]['title']='Changed after user approval'
            (folder/'storyboard.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'changed after approval'):
                validate_approval(folder)

    def test_hitl_rejects_unapproved_layout_or_animation_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'human-test';folder.mkdir()
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            deck=json.loads((ROOT/'decks/demo/deck.json').read_text())
            plan['deck_id']='human-test';deck['id']='human-test'
            (folder/'storyboard.json').write_text(json.dumps(plan))
            approve(folder,'Duyệt bố cục như đề xuất')
            deck['slides'][1]['type']='section'
            (folder/'deck.json').write_text(json.dumps(deck))
            with self.assertRaisesRegex(ValueError,'layout changed'):
                check_deck_against_plan(folder)
            deck['slides'][1]['type']='cards'
            deck['slides'][1]['cards'][-1]['reveal']='static'
            (folder/'deck.json').write_text(json.dumps(deck))
            with self.assertRaisesRegex(ValueError,'animation sequence changed'):
                check_deck_against_plan(folder)

    def test_plain_thanks_slogan_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            approval=json.loads((ROOT/'decks/demo/approval.json').read_text())
            deck=json.loads((ROOT/'decks/demo/deck.json').read_text())
            plan['deck_id']=folder.name;approval['deck_id']=folder.name
            approval['approval_channel']='chat';approval['approved_by']='user'
            approval['approval_quote']='Chấp thuận bố cục'
            approval['storyboard_sha256']=digest(plan)
            deck['id']=folder.name
            deck['slides'][-1]['subtitle']='Lịch sử là mạch nối'
            for name,data in [('storyboard.json',plan),('approval.json',approval),('deck.json',deck)]:
                (folder/name).write_text(json.dumps(data,ensure_ascii=False))
            (folder/'sources.json').write_text((ROOT/'decks/demo/sources.json').read_text())
            with self.assertRaisesRegex(ValueError,'thanks subtitle is a slogan'):
                validate(folder/'deck.json')

    def test_native_powerpoint_fade_trigger_and_morph_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            inp=tmp/'in.pptx';out=tmp/'out.pptx'
            prs=Presentation();blank=prs.slide_layouts[6]
            slide=prs.slides.add_slide(blank)
            from pptx.util import Inches
            for i in range(3):
                shape=slide.shapes.add_textbox(Inches(.3+i),Inches(.3),Inches(1.6),Inches(.5))
                shape.text=f'Animated text {i}'
                shape.name=f'CLICK_G{1 if i<2 else 2}_text_{i}'
            for i in range(2):
                slide=prs.slides.add_slide(blank)
                shape=slide.shapes.add_shape(1,Inches(1+i*.75),Inches(1),Inches(2+i),Inches(2+i))
                shape.name='!!historical_subject'
            prs.save(inp)
            patch(inp,out,{3})
            ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
            with ZipFile(out) as z:
                root=etree.fromstring(z.read('ppt/slides/slide1.xml'))
                fx=root.xpath('.//p:cTn[@presetClass="entr"]',namespaces=ns)
                self.assertEqual([f.get('nodeType') for f in fx],['clickEffect','withEffect','clickEffect'])
                self.assertTrue(all(f.get('presetID')=='10' for f in fx))
                self.assertEqual(len(root.xpath('.//p:bldLst/p:bldP',namespaces=ns)),3)
                root3=etree.fromstring(z.read('ppt/slides/slide3.xml'))
                self.assertTrue(root3.xpath('.//*[local-name()="morph"]'))

    def test_morph_requires_real_geometry_change(self):
        from pptx.util import Inches
        from pptx.enum.shapes import MSO_SHAPE
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);prs=Presentation();layout=prs.slide_layouts[6]
            for i in range(2):
                sl=prs.slides.add_slide(layout)
                sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(1),Inches(1),Inches(2),Inches(2))
                sh.name='!!same_frame'
            inp=tmp/'in.pptx';prs.save(inp)
            with self.assertRaisesRegex(ValueError,'changes neither framing nor focus'):
                patch(inp,tmp/'out.pptx',{2})

    def test_storyboard_must_propose_real_layout_and_reveals(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'example';folder.mkdir()
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            plan['deck_id']='example'
            plan['slides'][1]['reveal_sequence']=['static','static','static']
            (folder/'storyboard.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'presenter On Click'):
                validate_plan(folder)

    def test_human_approved_storyboard_can_create_matching_skeleton(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'decks').mkdir()
            folder=new_deck('approved-test','Final storyboard title',slides=3,root=root)
            plan=json.loads((folder/'storyboard.json').read_text())
            for index,sl in enumerate(plan['slides']):
                sl['takeaway']='A specific clear evidence-based takeaway'
                sl['visual']='Portrait/diagram placed on the right'
                sl['composition']='Two columns, left text, right visual'
                if index==1:
                    sl['layout']='cards'
                    sl['title']='Three pieces of evidence'
                    sl['content_units']=3
                    sl['reveal_sequence']=['auto','click','click']
            (folder/'storyboard.json').write_text(json.dumps(plan,ensure_ascii=False))
            approve(folder,'Duyệt bố cục 3 slide')
            new_deck('approved-test','',root=root,from_approved_plan=True)
            deck=json.loads((folder/'deck.json').read_text())
            self.assertEqual(len(deck['slides']),3)
            self.assertEqual(deck['slides'][1]['type'],'cards')
            self.assertEqual([x['reveal'] for x in deck['slides'][1]['cards']],['auto','click','click'])
            self.assertTrue(check_deck_against_plan(folder))

    def test_storyboard_rejects_missing_reveal_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'plan-test';folder.mkdir()
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            plan['deck_id']='plan-test'
            plan['slides'][1]['reveal_sequence']=['auto','click']
            (folder/'storyboard.json').write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'one entry per content unit'):
                validate_plan(folder)

        mandatory=['AGENTS.md','SKILL.md','README.md','CHAT_PROMPT.md',
          'scripts/build_deck.cjs','scripts/run_pipeline.py','scripts/qa_pptx.py',
          'scripts/patch_animations.py','scripts/render_deck.py',
          'scripts/check_storyboard.py','scripts/render_storyboard.py','schemas/storyboard.schema.json',
          'schemas/deck.schema.json','.github/workflows/build-slides.yml']
        for file in mandatory:
            self.assertTrue((ROOT/file).is_file(),file)

    def test_balanced_diagrams_are_general_not_three_item_special_cases(self):
        # Pure geometry tests, independent of any history/politics vocabulary.
        script = """
const {planDiagram}=require('./scripts/diagram_geometry.cjs');
const box={x:1.05,y:2.13,w:11.23,h:4.6};
console.log(JSON.stringify([
  planDiagram('peers',3,box),
  planDiagram('peers',5,box),
  planDiagram('peers',7,box),
  planDiagram('reciprocal',3,box),
  planDiagram('hierarchy',6,box)
]));
"""
        proc=subprocess.run(['node','-e',script],cwd=ROOT,check=True,
                            text=True,capture_output=True)
        plans=json.loads(proc.stdout)
        for plan,expected_rows in zip(plans[:3],([3],[3,2],[4,3])):
            by_row={}
            for tile in plan['grid']['tiles']:
                by_row.setdefault(tile['row'],[]).append(tile)
            self.assertEqual([len(by_row[i]) for i in sorted(by_row)],expected_rows)
            for tiles in by_row.values():
                left=min(t['x'] for t in tiles)
                right=max(t['x']+t['w'] for t in tiles)
                self.assertAlmostEqual((left+right)/2,plan['grid']['centerX'],places=4)
            self.assertLess(max(t['w'] for t in plan['grid']['tiles'])-
                            min(t['w'] for t in plan['grid']['tiles']),1e-6)
        interaction=plans[3]
        self.assertEqual(interaction['relationship'],'reciprocal')
        tiles=interaction['grid']['tiles']
        self.assertEqual({t['row'] for t in tiles},{0,1,2})
        self.assertLess(interaction['root']['x']+interaction['root']['w'],
                        min(t['x'] for t in tiles))
        self.assertLess(abs(interaction['root']['y']+interaction['root']['h']/2 -
            (min(t['y'] for t in tiles)+max(t['y']+t['h'] for t in tiles))/2),0.2)
        self.assertEqual(plans[4]['relationship'],'hierarchy')

    def test_human_approval_locks_semantic_relationship(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'semantic-test'
            folder.mkdir()
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            deck=json.loads((ROOT/'decks/demo/deck.json').read_text())
            plan['deck_id']=folder.name
            deck['id']=folder.name
            plan['slides'][3]['diagram_relationship']='reciprocal'
            deck['slides'][3]['diagram_relationship']='reciprocal'
            (folder/'storyboard.json').write_text(json.dumps(plan,ensure_ascii=False))
            approve(folder,'Duyệt sơ đồ quan hệ tương hỗ')
            (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False))
            self.assertTrue(check_deck_against_plan(folder))
            deck['slides'][3]['diagram_relationship']='hierarchy'
            (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False))
            with self.assertRaisesRegex(ValueError,'semantic diagram relationship changed'):
                check_deck_against_plan(folder)

    def test_storyboard_rejects_unknown_relationship(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'semantic-test'
            folder.mkdir()
            plan=json.loads((ROOT/'decks/demo/storyboard.json').read_text())
            plan['deck_id']=folder.name
            plan['slides'][3]['diagram_relationship']='random_boxes'
            (folder/'storyboard.json').write_text(json.dumps(plan,ensure_ascii=False))
            with self.assertRaisesRegex(ValueError,'not one of'):
                validate_plan(folder)

    def test_reciprocal_diagram_pptx_integration_and_divider_qa(self):
        # Build and inspect real slide shapes; a pure geometry test is not
        # sufficient to catch mis-sized or ungrouped objects in PowerPoint.
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'semantic-qa'
            folder.mkdir()
            deck={
              'id':'semantic-qa','title':'Semantic diagram regression',
              'requested_slide_count':3,'language':'vi',
              'slides':[
                {'type':'cover','title':'Semantic diagram regression',
                 'subtitle':'Real PowerPoint composition test',
                 'notes':'Test cover for a reproducible composition example.'},
                {'type':'diagram','title':'An interaction between fields',
                 'subtitle':'Each field is a peer and interacts with the central concept.',
                 'diagram_relationship':'reciprocal',
                 'root':'SHARED CONTEXT','group_label':'RECIPROCAL INTERACTION',
                 'items':['SCIENCE','POLICY','ECONOMY'],
                 'bottom':'JOINT OUTCOME','caption':'INTERACTION TEST',
                 'notes':'The diagram shows two-way influence, rather than an accidental hierarchy.'},
                {'type':'thanks','title':'Thank you','subtitle':'Questions welcome',
                 'notes':'The closing page is neutral and does not invent slogans.'}
              ]
            }
            (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False))
            build=subprocess.run(['node',str(ROOT/'scripts/build_deck.cjs'),str(folder)],
                cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(build.returncode,0,build.stderr)
            base=folder/'dist'/'semantic-qa.base.pptx'
            out=folder/'dist'/'semantic-qa.pptx'
            patch(base,out,set())
            conf=folder/'dist'/'qa-config.json'
            report=folder/'dist'/'qa-report.json'
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/qa_pptx.py'),
                str(out),'--spec',str(conf),'--report',str(report),'--strict'],
                cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stdout+'\n'+proc.stderr)
            info=json.loads(report.read_text())
            self.assertEqual(info['metrics']['semantic_diagrams_checked'],1)
            self.assertEqual(info['metrics']['horizontal_rules'],0)
            slide=Presentation(out).slides[1]
            frames=[s for s in slide.shapes if s.name.startswith('CLICK_G1_item')
                    and s.name.endswith('_panel')]
            self.assertEqual(len(frames),3)
            roots=[s for s in slide.shapes if s.name=='AUTO_G0_diagramroot_panel']
            self.assertEqual(len(roots),1)
            self.assertLess(roots[0].left+roots[0].width,min(s.left for s in frames))

    def test_horizontal_rule_detector_catches_pptxgenjs_style_zero_height_shape(self):
        # PptxGenJS can serialize an h=0 line as AUTO_SHAPE, not LINE.
        # The QA rule must look at geometry rather than the shape type alone.
        from pptx.util import Inches
        from pptx.enum.shapes import MSO_CONNECTOR
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            p=tmp/'rules.pptx'
            prs=Presentation()
            slide=prs.slides.add_slide(prs.slide_layouts[6])
            line=slide.shapes.add_connector(
                MSO_CONNECTOR.STRAIGHT, Inches(.8),Inches(3),
                Inches(9.8),Inches(3))
            line.name='DECO_unnecessary_line'
            prs.save(p)
            cfg=tmp/'qa.json';report=tmp/'report.json'
            cfg.write_text(json.dumps({'max_decorative_dividers':0}))
            def check():
                proc=subprocess.run([sys.executable,str(ROOT/'scripts/qa_pptx.py'),
                    str(p),'--spec',str(cfg),'--report',str(report),'--strict'],
                    cwd=ROOT,text=True,capture_output=True)
                return proc, json.loads(report.read_text())
            result,info=check()
            self.assertNotEqual(result.returncode,0,result.stdout)
            self.assertIn('too_many_decorative_dividers',
                          [e['reason'] for e in info['errors']])
            self.assertEqual(info['metrics']['horizontal_rules'],1)
            line.name='STRUCTURAL_timeline_axis'
            prs.save(p)
            result,info=check()
            self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
            self.assertEqual(info['metrics']['horizontal_rules'],1)

if __name__=='__main__':
    unittest.main(verbosity=2)
