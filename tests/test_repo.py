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
                spec=json.loads((root/'decks/count-test/deck.json').read_text())
                self.assertEqual(spec['requested_slide_count'],slides)
                self.assertEqual(len(spec['slides']),slides)
                if slides>1:
                    self.assertEqual(spec['slides'][-1]['type'],'thanks')

    def test_unfilled_skeleton_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'decks').mkdir()
            new_deck('count-test','Test of presentation length',slides=15,root=root)
            with self.assertRaisesRegex(ValueError,'unresolved TODO placeholder'):
                validate(root/'decks/count-test/deck.json')

    def test_core_files_present(self):
        mandatory=['AGENTS.md','SKILL.md','README.md','CHAT_PROMPT.md',
          'scripts/build_deck.cjs','scripts/run_pipeline.py','scripts/qa_pptx.py',
          'scripts/patch_animations.py','scripts/render_deck.py',
          'schemas/deck.schema.json','.github/workflows/build-slides.yml']
        for file in mandatory:
            self.assertTrue((ROOT/file).is_file(),file)

if __name__=='__main__':
    unittest.main(verbosity=2)
