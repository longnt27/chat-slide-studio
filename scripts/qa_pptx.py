#!/usr/bin/env python3
"""Production slide-deck structural QA. Visual review remains mandatory.

Usage:
  python qa_pptx.py deck.pptx --spec qa-spec.json --report qa.json --strict

Optional dependencies: python-pptx, lxml. No network access required.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import hashlib
import posixpath
from pathlib import Path
import re
import sys
from zipfile import ZipFile

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
MORPH = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
NS = {'p': P, 'morph': MORPH, 'mc': MC}
EMU = 914400


def b(sh):
    return (sh.left / EMU, sh.top / EMU,
            (sh.left + sh.width) / EMU, (sh.top + sh.height) / EMU)


def overlap_area(u, v):
    return max(0., min(u[2], v[2]) - max(u[0], v[0])) * max(0., min(u[3], v[3]) - max(u[1], v[1]))


def center(sh):
    return (sh.left + sh.width / 2) / EMU


def load_conf(fname):
    return json.loads(Path(fname).read_text(encoding='utf-8')) if fname else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('deck', type=Path)
    ap.add_argument('--spec', type=Path, help='Optional deck-specific QA policy (JSON)')
    ap.add_argument('--report', type=Path, help='Write machine-readable JSON report')
    ap.add_argument('--strict', action='store_true', help='Nonzero exit for structural failures')
    args = ap.parse_args()
    config = load_conf(args.spec)
    errors, warnings = [], []
    metrics = {'slides': 0, 'notes': 0, 'photos': 0, 'semantic_click_steps': 0,
               'auto_groups': 0, 'morph_transitions': 0, 'animated_shape_ids': 0,
               'horizontal_rules': 0, 'semantic_diagrams_checked': 0}

    def error(slide, reason, detail=''):
        errors.append({'slide': slide, 'reason': reason, 'detail': str(detail)})

    def warn(slide, reason, detail=''):
        warnings.append({'slide': slide, 'reason': reason, 'detail': str(detail)})

    try:
        prs = Presentation(args.deck)
    except Exception as exc:
        print('FATAL: invalid PowerPoint:', exc, file=sys.stderr)
        return 2
    metrics['slides'] = len(prs.slides)
    if config.get('expected_slides') is not None and metrics['slides'] != int(config['expected_slides']):
        error(0, 'slide_count', f"Expected {config['expected_slides']}, found {metrics['slides']}")

    sw = prs.slide_width / EMU
    sh = prs.slide_height / EMU
    try:
        archive = ZipFile(args.deck)
        bad = archive.testzip()
        if bad:
            error(0, 'zip_integrity', bad)
    except Exception as exc:
        error(0, 'zip_integrity', exc)
        archive = None

    all_names = {}
    morph_by_slide = {}
    morph_picture_bytes = {}
    morph_evidence = []
    max_overlap = float(config.get('max_text_overlap_area_in2', .018))

    for number, slide in enumerate(prs.slides, 1):
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text
            if notes.strip():
                metrics['notes'] += 1
        else:
            notes = ''
        if config.get('require_speaker_notes', False) and not notes.strip():
            error(number, 'missing_speaker_notes')
        if config.get('require_source_notes', False) and '[Sources]' not in notes:
            error(number, 'missing_source_notes')

        photos = [shape for shape in slide.shapes if shape.shape_type == MSO_SHAPE_TYPE.PICTURE]
        metrics['photos'] += len(photos)
        # Count long horizontal RULE shapes, not arrows or panel borders.
        # A single line may encode an actual timeline; repeated ornaments
        # should not turn a slide into a Markdown README.
        long_horizontal_rules = [
            x for x in slide.shapes
            if x.shape_type == MSO_SHAPE_TYPE.LINE and
            x.width/EMU >= 0.75 and abs(x.height/EMU) <= 0.045
        ]
        metrics['horizontal_rules'] += len(long_horizontal_rules)
        max_rules = config.get('max_decorative_dividers')
        if max_rules is not None and len(long_horizontal_rules) > int(max_rules):
            error(number, 'too_many_decorative_dividers',
                  f'{len(long_horizontal_rules)} horizontal lines; limit {max_rules}')
        texts = [shape for shape in slide.shapes if shape.has_text_frame and shape.text.strip()]

        for shape in slide.shapes:
            shape_b = b(shape)
            tolerance = .025
            if (shape_b[0] < -tolerance or shape_b[1] < -tolerance or
                    shape_b[2] > sw+tolerance or shape_b[3] > sh+tolerance):
                error(number, 'out_of_canvas', f"{shape.name} {tuple(round(n,2) for n in shape_b)}")

        for ix, a in enumerate(texts):
            for z in texts[ix+1:]:
                area = overlap_area(b(a), b(z))
                if area <= max_overlap:
                    continue
                # Text in paired deliberately overlaid title components can be exempted.
                exempt = any(item.get('slide') == number and (
                    (item.get('contains_a','') in a.text and item.get('contains_b','') in z.text) or
                    (item.get('contains_b','') in a.text and item.get('contains_a','') in z.text)
                ) for item in config.get('allow_text_overlap', []))
                if not exempt:
                    error(number, 'text_text_overlap', f'{a.text[:32]!r} versus {z.text[:32]!r}, {area:.3f} sq in')

        if not archive:
            continue
        filename = f'ppt/slides/slide{number}.xml'
        try:
            root = etree.fromstring(archive.read(filename))
        except Exception as exc:
            error(number, 'missing_or_invalid_slide_xml', exc)
            continue

        id_names = {}
        for shape in root.xpath('.//p:sp | .//p:pic | .//p:graphicFrame | .//p:cxnSp', namespaces=NS):
            props = shape.find('.//{%s}cNvPr' % P)
            if props is not None and props.get('id'):
                id_names[int(props.get('id'))] = props.get('name','')
        all_names[number] = list(id_names.values())
        # Compare actual embedded source bytes, not merely !! object names.
        # A native Morph should interpolate the SAME source image, not fade
        # between differently cropped/letterboxed JPEG reconstructions.
        relationship_path=f'ppt/slides/_rels/slide{number}.xml.rels'
        ridmap={}
        if relationship_path in archive.namelist():
            rel_root=etree.fromstring(archive.read(relationship_path))
            ridmap={node.get('Id'):node.get('Target') for node in rel_root}
        picture_digest={}
        for pic in root.xpath('.//p:pic',namespaces=NS):
            props=pic.find('.//{%s}cNvPr'%P)
            if props is None or not props.get('name','').startswith('!!'):continue
            name=props.get('name')
            embeds=pic.xpath('.//*[local-name()="blip"]/@*[local-name()="embed"]')
            if len(embeds)!=1 or embeds[0] not in ridmap:
                error(number,'morph_image_has_no_embedded_asset',name)
                continue
            media_file=posixpath.normpath(posixpath.join('ppt/slides',ridmap[embeds[0]]))
            if media_file not in archive.namelist():
                error(number,'morph_image_file_missing',media_file)
            else:
                picture_digest[name]=hashlib.sha256(archive.read(media_file)).hexdigest()
        morph_picture_bytes[number]=picture_digest
        existing = set(id_names)
        targets = set()
        for v in root.xpath('.//p:spTgt', namespaces=NS):
            try:
                sid = int(v.get('spid'))
                targets.add(sid)
                if sid not in existing:
                    error(number, 'invalid_animation_target', sid)
            except (TypeError, ValueError):
                error(number, 'invalid_animation_target', str(v.attrib))
        metrics['animated_shape_ids'] += len(targets)

        automatic = {sid for sid,name in id_names.items() if name.startswith('AUTO_G0_')}
        clicks = defaultdict(set)
        for sid, name in id_names.items():
            match = re.match(r'^CLICK_G(\d+)_', name)
            if match:
                clicks[int(match.group(1))].add(sid)
        for g in sorted(clicks):
            if g <= 0:
                error(number, 'invalid_click_group_number', g)
        expected = ([automatic] if automatic else []) + [clicks[g] for g in sorted(clicks)]
        if automatic:
            metrics['auto_groups'] += 1
        metrics['semantic_click_steps'] += len(clicks)

        for sid in (automatic | set().union(*clicks.values()) if clicks else automatic):
            if sid not in targets:
                error(number, 'unanimated_group_member', f"{id_names.get(sid)} (shape {sid})")

        seq = root.xpath('.//p:cTn[@nodeType="mainSeq"]', namespaces=NS)
        if automatic or clicks:
            if len(seq) != 1:
                error(number, 'missing_semantic_main_sequence', len(seq))
            else:
                steps = seq[0].xpath('./p:childTnLst/p:par', namespaces=NS)
                if len(steps) != len(expected):
                    error(number, 'click_step_count', f'expected {len(expected)}, got {len(steps)}')
                for index, (step, group) in enumerate(zip(steps, expected)):
                    actual = {int(t.get('spid')) for t in step.xpath('.//p:spTgt', namespaces=NS)}
                    if actual != group:
                        error(number, 'semantic_group_split_or_extra_shapes',
                              f'step {index}: missing {group-actual}, extra {actual-group}')
                    effects = step.xpath('.//p:animEffect', namespaces=NS)
                    effect_filters = {e.get('filter') for e in effects}
                    if len(effect_filters) > 1:
                        error(number, 'mixed_peer_effects', str(effect_filters))
                    durations = {n.get('dur') for n in step.xpath('.//p:cTn[@nodeType="withEffect"]', namespaces=NS)}
                    if len(durations) > 1:
                        error(number, 'mixed_peer_durations', str(durations))
                    # Native PowerPoint 16.0 animation oracle: entrance Fade=10,
                    # first on-click effect node=clickEffect; all siblings
                    # start With Previous. The automatic first group uses
                    # afterEffect at time zero, not an extra empty click step.
                    time_nodes = step.xpath('.//p:cTn[@presetClass="entr"]', namespaces=NS)
                    expected_types = (['afterEffect'] if index == 0 and automatic else ['clickEffect'])
                    expected_types += ['withEffect'] * (len(group) - 1)
                    actual_types = [effect.get('nodeType') for effect in time_nodes]
                    if actual_types != expected_types:
                        error(number, 'invalid_native_animation_trigger',
                            f'group {index}: expected {expected_types}, got {actual_types}')
                    if len(time_nodes) != len(group):
                        error(number, 'missing_native_entrance_effects',
                            f'group {index}: {len(time_nodes)} vs {len(group)}')
                    if any(effect.get('presetID')!='10' for effect in time_nodes):
                        error(number, 'wrong_native_fade_preset',
                            'PowerPoint-authored Fade has presetID=10')
                    if len(effects)!=len(group) or any(effect.get('filter')!='fade' for effect in effects):
                        error(number, 'native_fade_missing_or_wrong_filter',
                              f'group {index}: {len(effects)} effects for {len(group)} shapes')
                    first_condition=step.xpath('./p:cTn/p:stCondLst/p:cond',namespaces=NS)
                    expected_delay='0' if index==0 and automatic else 'indefinite'
                    if len(first_condition)!=1 or first_condition[0].get('delay')!=expected_delay:
                        error(number,'wrong_click_vs_auto_timing',
                              f'group {index}: expected delay={expected_delay}')
                    observed_ids=[int(node.get('id')) for node in step.xpath('.//p:cTn',namespaces=NS)]
                    if len(observed_ids)!=len(set(observed_ids)):
                        error(number,'duplicate_timing_node_ids',observed_ids)
        # Native PowerPoint build-list entries are only for text-bearing
        # shapes. Pictures and card borders must not appear here.
        text_shape_ids=set()
        for shp in root.xpath('.//p:sp',namespaces=NS):
            nv=shp.find('.//{%s}cNvPr'%P)
            if nv is not None and nv.get('id') and shp.find('{%s}txBody'%P) is not None:
                text_shape_ids.add(int(nv.get('id')))
        targets_group=automatic | (set().union(*clicks.values()) if clicks else set())
        expected_builds=text_shape_ids & targets_group
        actual_builds={int(x.get('spid')) for x in root.xpath('.//p:bldLst/p:bldP',namespaces=NS)}
        if expected_builds!=actual_builds:
            error(number,'native_text_build_list_mismatch',
                  f'missing {expected_builds-actual_builds}, extra {actual_builds-expected_builds}')
        if config.get('click_note_matching', False):
            cues = re.findall(r'\bClick\s+\d+\s*:', notes, flags=re.I)
            if len(cues) != len(clicks):
                error(number, 'click_notes_not_matching', f'{len(clicks)} groups but {len(cues)} cues')

        if root.xpath('./p:transition[@advTm]', namespaces=NS):
            warn(number, 'automatic_slide_advance', 'Check intended presenter control')
        morphs = root.xpath('.//morph:morph', namespaces=NS)
        morph_by_slide[number] = bool(morphs)
        if morphs:
            metrics['morph_transitions'] += 1
            if number <= 1:
                error(number, 'morph_on_first_slide')
            if not root.xpath('./mc:AlternateContent', namespaces=NS):
                warn(number, 'morph_missing_fade_fallback')
            # Slide destination must contain matching semantic counterpart.
            previous = {x for x in all_names.get(number-1,[]) if x.startswith('!!')}
            current = {x for x in all_names.get(number,[]) if x.startswith('!!')}
            matches = previous & current
            if not matches:
                error(number, 'morph_without_adjacent_subject_match',
                      f'previous: {sorted(previous)}, current: {sorted(current)}')
            if len(matches) > 3:
                warn(number, 'morph_too_many_objects', sorted(matches))
            for paired in matches:
                old_sh=next((shp for shp in prs.slides[number-2].shapes if shp.name==paired),None)
                new_sh=next((shp for shp in slide.shapes if shp.name==paired),None)
                if old_sh is not None and new_sh is not None:
                    old_box=b(old_sh);new_box=b(new_sh)
                    travel=((center(old_sh)-center(new_sh))**2+
                           (((old_box[1]+old_box[3])/2)-((new_box[1]+new_box[3])/2))**2)**0.5
                    scale=max(old_sh.width/new_sh.width,new_sh.width/old_sh.width,
                              old_sh.height/new_sh.height,new_sh.height/old_sh.height)
                    morph_evidence.append({'from_slide':number-1,'to_slide':number,
                        'subject':paired,'travel_in':round(travel,3),
                        'scale_ratio':round(scale,3),
                        'powerpoint_playback_verified':False})
                old_hash=morph_picture_bytes.get(number-1,{}).get(paired)
                new_hash=morph_picture_bytes[number].get(paired)
                if old_hash and new_hash and old_hash!=new_hash:
                    error(number,'morph_picture_source_changed',
                          paired+' uses two different encoded pictures')

    for item in config.get('centered_labels', []):
        number = int(item['slide'])
        label = item['text']
        matching = [s for s in prs.slides[number-1].shapes
                    if s.has_text_frame and s.text.strip() == label]
        if len(matching) != 1:
            error(number, 'centered_label_missing_or_duplicated', label)
            continue
        shape = matching[0]
        if shape.text_frame.paragraphs[0].alignment != PP_ALIGN.CENTER:
            error(number, 'not_really_centered', label)
        tolerance = float(item.get('tolerance_in',.08))
        desired = float(item['center_x'])
        if abs(center(shape)-desired) > tolerance:
            error(number, 'centered_label_wrong_axis', f'{label}: actual {center(shape):.3f}, target {desired:.3f}')

    for row in config.get('card_rows', []):
        number = int(row['slide'])
        labels = row.get('shape_names',[])
        found = []
        for label in labels:
            matches = [s for s in prs.slides[number-1].shapes if s.name == label]
            if len(matches) != 1:
                error(number, 'card_shape_missing_or_duplicated', f'{label} count={len(matches)}')
            else:
                found.append(matches[0])
        if len(found) < 2:
            continue
        found.sort(key=lambda x:x.left)
        widths=[s.width/EMU for s in found]
        gaps=[(found[i+1].left - found[i].left - found[i].width)/EMU for i in range(len(found)-1)]
        tol=float(row.get('tolerance_in', .09))
        if max(widths)-min(widths)>tol:
            error(number, 'unequal_card_widths', widths)
        if len(gaps)>1 and max(gaps)-min(gaps)>tol:
            error(number, 'unequal_card_gaps', gaps)
        left=float(row.get('container_left',0.))
        right=float(row.get('container_right',sw))
        margins=(found[0].left/EMU-left, right-(found[-1].left+found[-1].width)/EMU)
        if abs(margins[0]-margins[1])>tol:
            error(number, 'unbalanced_card_margins', margins)

    # Verify composition geometry for deliberately declared relationships.
    # This checks row symmetry and left/right semantics, never a hardcoded
    # screenshot-specific label or item count.
    for diagram in config.get('diagram_relationships', []):
        number=int(diagram['slide'])
        page=prs.slides[number-1]
        labels=diagram['item_shape_names']
        peer_axis=float(diagram['peer_axis_x'])
        tol=float(diagram.get('tolerance_in',0.095))
        found=[]
        for name in labels:
            matches=[shp for shp in page.shapes if shp.name==name]
            if len(matches)!=1:
                error(number,'missing_semantic_diagram_item',f'{name}: {len(matches)}')
            else:
                found.append(matches[0])
        if len(found)!=len(labels):
            continue
        metrics['semantic_diagrams_checked']+=1
        widths=[x.width/EMU for x in found]
        if max(widths)-min(widths)>tol:
            error(number,'diagram_peer_widths_differ',widths)
        rows=defaultdict(list)
        for sh_obj in found:
            rows[round(sh_obj.top/EMU,2)].append(sh_obj)
        for y,row in rows.items():
            left=min(x.left/EMU for x in row)
            right=max((x.left+x.width)/EMU for x in row)
            if abs((left+right)/2-peer_axis)>tol:
                error(number,'diagram_peer_row_not_centered',
                      f'y={y}: midpoint {(left+right)/2:.3f}, expected {peer_axis:.3f}')
        relation=diagram.get('relationship')
        if relation=='reciprocal':
            roots=[shp for shp in page.shapes
                   if shp.name==diagram.get('root_shape_name')]
            if len(roots)!=1:
                error(number,'reciprocal_root_missing')
            else:
                root=roots[0]
                if (root.left+root.width)/EMU >= min(x.left/EMU for x in found)-0.30:
                    error(number,'reciprocal_not_two_sided',
                          'Root and equal peers must occupy distinct left/right regions')
                peer_center_y=(min(x.top/EMU for x in found)+
                    max((x.top+x.height)/EMU for x in found))/2
                root_center_y=(root.top+root.height/2)/EMU
                if abs(root_center_y-peer_center_y)>0.38:
                    error(number,'reciprocal_vertical_imbalance',
                          f'root {root_center_y:.2f} vs group {peer_center_y:.2f}')
        elif relation not in ('peers','hierarchy'):
            error(number,'unsupported_diagram_relationship',relation)

    expected_morph=config.get('expected_morph_slides')
    if expected_morph is not None:
        observed={n for n,used in morph_by_slide.items() if used}
        if observed!=set(expected_morph):
            error(0,'morph_transition_set_mismatch',
                  f'expected {sorted(expected_morph)}, actual {sorted(observed)}')

    # A long deck with zero presenter-controlled entrances is not an
    # animated presentation; the renderer should not silently claim it is.
    required_clicks=config.get('min_click_groups',0)
    if required_clicks and metrics['semantic_click_steps']<required_clicks:
        error(0,'insufficient_presenter_animation',
              f'expected at least {required_clicks}, found {metrics["semantic_click_steps"]}')
    max_morph = config.get('morph_max_fraction')
    if max_morph is not None and len(prs.slides)>1 and metrics['morph_transitions'] / (len(prs.slides)-1) > float(max_morph):
        error(0, 'excessive_morph_transitions', metrics['morph_transitions'])

    audit_file = config.get('image_audit')
    if audit_file:
        audit_path = Path(audit_file)
        if not audit_path.is_absolute() and args.spec:
            audit_path = args.spec.parent / audit_path
        if not audit_path.exists():
            error(0,'missing_image_audit',audit_path)
        else:
            try:
                audit = json.loads(audit_path.read_text(encoding='utf-8'))
                if isinstance(audit,dict):
                    audit=audit.get('images',audit.get('assets',[]))
                for entry in audit:
                    if entry.get('mode')=='cover' and not entry.get('decorative',False):
                        error(entry.get('slide',0),'unapproved_image_crop',entry.get('key',entry.get('source','')))
            except Exception as exc:
                error(0,'invalid_image_audit',exc)

    report = {
        'deck': str(args.deck),
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'metrics':metrics,
        'errors':errors,'warnings':warnings,
        'morph_evidence':morph_evidence,
        'machine_passed':not errors,
        'visual_review_required':True,
        'native_powerpoint_playback_tested':False
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('QA:', 'PASS' if not errors else 'FAIL',
          f'| {metrics["slides"]} slides, {metrics["notes"]} notes, '
          f'{metrics["semantic_click_steps"]} click groups, {metrics["morph_transitions"]} Morph, '
          f'{len(errors)} errors, {len(warnings)} warnings')
    for issue in errors[:30]:
        print('ERROR',issue['slide'],issue['reason'],issue['detail'])
    for issue in warnings[:15]:
        print('WARN ',issue['slide'],issue['reason'],issue['detail'])
    return 1 if errors and args.strict else 0

if __name__=='__main__':
    sys.exit(main())
