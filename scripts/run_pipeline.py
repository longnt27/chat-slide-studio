#!/usr/bin/env python3
"""Single command behind the GitHub CI workflow and local reproduction.

Builds editable PPTX, selective Morph / click animations, PDF, PNG previews,
image credits, and machine QA. Does NOT certify PowerPoint playback.
"""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
from check_storyboard import validate_plan, validate_production_plan, digest
from presentation_profile import compile_route, motion_of


def select_diff_base(ref_name, push_before):
    """Cover the ENTIRE pushed range on main, not only HEAD~1.

    A fast-forward merge can move main over many commits. Looking at just
    HEAD~1 (often docs only) would incorrectly skip engine/deck QA.
    """
    if ref_name != 'main':
        return None
    if re.fullmatch(r'[0-9a-fA-F]{40}', push_before or '') and set(push_before) != {'0'}:
        return push_before
    return 'HEAD~1'



def step(*argv, cwd=ROOT, env=None):
    print('+', ' '.join(map(str,argv)),flush=True)
    subprocess.run([str(v) for v in argv],check=True,cwd=cwd,env=env)


def build(deck_dir):
    deck_dir=Path(deck_dir).resolve()
    if not (deck_dir/'deck.json').exists():
        raise ValueError(f'Missing deck.json: {deck_dir}')
    spec=json.loads((deck_dir/'deck.json').read_text(encoding='utf8'))
    slug=spec['id']
    branch=os.environ.get('GITHUB_REF_NAME')
    if branch and branch!='main' and spec.get('branch') and branch!=spec['branch']:
        raise ValueError('Deck %s belongs to branch %s, but CI is building %s' %
                         (slug,spec['branch'],branch))
    internal_plan=validate_plan(deck_dir)
    production_contract=validate_production_plan(deck_dir,internal_plan)
    expected=spec.get('requested_slide_count')
    if not isinstance(expected,int) or isinstance(expected,bool) or len(spec['slides'])!=expected:
        raise ValueError(f"Slide count mismatch: requested {expected}, authored {len(spec['slides'])}")
    if deck_dir.name!=slug:
        raise ValueError(f'Deck folder must match deck.id: {deck_dir.name} vs {slug}')
    if not deck_dir.is_relative_to(ROOT/'decks'):
        raise ValueError(f'Deck must be under {ROOT}/decks')
    dist=deck_dir/'dist'
    dist.mkdir(exist_ok=True)
    python=sys.executable
    step(python,ROOT/'scripts/check_spec.py',deck_dir/'deck.json')
    is_revision=(deck_dir/'revision_requests.json').exists()
    if is_revision:
        step(python,ROOT/'scripts/revision_qa.py',deck_dir,
             '--report',dist/'revision-qa.json')
    # Compile the physical visit order from the approved logical story.
    # TOC revisits are real PPTX/PDF pages but not new content chapters.
    step(python,ROOT/'scripts/presentation_profile.py',deck_dir/'deck.json')
    route=json.loads((dist/'slide-route.json').read_text(encoding='utf-8'))
    step(python,ROOT/'scripts/fetch_assets.py',deck_dir/'sources.json',
         '--out',deck_dir/'verified-assets','--strict') if json.loads(
            (deck_dir/'sources.json').read_text(encoding='utf8')).get('assets') else None
    if not (deck_dir/'verified-assets'/'assets.json').exists():
        assets_dir=deck_dir/'verified-assets';assets_dir.mkdir(exist_ok=True)
        (assets_dir/'assets.json').write_text(json.dumps({'assets':[],'errors':[]}))
        (assets_dir/'credits.csv').write_text('id,filename,subject,author,license,license_url,source_page,download_url,sha256,width,height\n')
    env=os.environ.copy()
    # Honor locally preinstalled node modules for offline development; GitHub
    # CI runs `npm install` and never needs this fallback.
    step('node',ROOT/'scripts/build_deck.cjs',deck_dir,env=env)
    morph=','.join(str(n) for n in route['morph_physical_destinations'])
    target=dist/f'{slug}.pptx'
    animation_args=['--static'] if motion_of(spec)=='none' else ['--morph',morph]
    if spec.get('navigation') and motion_of(spec)!='none':
        animation_args.append('--hub-navigation')
    step(python,ROOT/'scripts/patch_animations.py',dist/f'{slug}.base.pptx',target,*animation_args)
    step(python,ROOT/'scripts/qa_pptx.py',target,'--spec',dist/'qa-config.json',
         '--report',dist/'qa-report.json','--strict')
    step(python,ROOT/'scripts/render_deck.py',target,'--out',dist/'preview',
         '--expected',route['physical_count'])
    shutil.copy2(dist/'preview'/f'{slug}.pdf',dist/f'{slug}.pdf')
    shutil.copy2(dist/'preview'/'montage.png',dist/'montage.png')
    if is_revision:
        step(python,ROOT/'scripts/visual_revision.py',deck_dir,
             '--report',dist/'revision-visual.json')
    shutil.copy2(deck_dir/'verified-assets'/'credits.csv',dist/'credits.csv')
    report=json.loads((dist/'qa-report.json').read_text(encoding='utf8'))
    if not report['machine_passed']:
        raise ValueError('Machine QA did not pass')
    deliverable={
      'deck':slug,'title':spec['title'],
      'slide_count':route['logical_count'],
      'logical_slide_count':route['logical_count'],
      'physical_slide_count':report['metrics']['slides'],
      'toc_revisit_count':route['revisit_count'],
      'tier':route['tier'],'animation_mode':route['animation_mode'],
      'slide_route':'slide-route.json',
      'requested_slide_count':expected,
      'files': [f'{slug}.pptx', f'{slug}.pdf','montage.png','credits.csv','qa-report.json','slide-route.json'] + (['revision-qa.json','revision-visual.json'] if is_revision else []),
      'click_groups':report['metrics']['semantic_click_steps'],
      'morph_transitions':report['metrics']['morph_transitions'],
      'machine_qa':'PASS',
      'visual_review':'REQUIRED (open rendered montage and individual slide PNGs)',
      'powerpoint_playback':'NOT VERIFIED (test Slide Show on Microsoft PowerPoint)',
      'internal_storyboard_sha256':digest(internal_plan),
      'plan_origin':production_contract['approval_channel'],
      'revision_acceptance':'PENDING USER REVIEW' if is_revision else 'NOT APPLICABLE'
    }
    (dist/'delivery.json').write_text(json.dumps(deliverable,ensure_ascii=False,indent=2),encoding='utf8')
    print('DELIVERABLE',json.dumps(deliverable,ensure_ascii=False),flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group()
    group.add_argument('--deck',help='Deck slug in decks/<slug>')
    group.add_argument('--all',action='store_true',help='Build every authored deck under decks/')
    group.add_argument('--changed',action='store_true',help='Build changed decks; internal plans are not user-facing artifacts')
    args=ap.parse_args()
    decks=sorted(p for p in (ROOT/'decks').iterdir() if (p/'deck.json').is_file())
    if args.deck:
        if args.deck not in [p.name for p in decks]:
            raise ValueError('Deck slug not found: '+args.deck)
        decks=[p for p in decks if p.name==args.deck]
    elif args.changed:
        # Chat HITL proposal commits include storyboard.json but NO deck.json.
        # Such commits may produce wireframe artifacts, but never a slide deck.
        # CI checks out full git history; this selection avoids rebuilding the
        # demo and accidentally delivering it on every proposal-only branch.
        diff_base=select_diff_base(
            os.environ.get('GITHUB_REF_NAME',''),
            os.environ.get('PUSH_BEFORE_SHA',''))
        if diff_base is None:
            cp=subprocess.run(['git','merge-base','HEAD','origin/main'],
                              cwd=ROOT,text=True,capture_output=True,check=True)
            diff_base=cp.stdout.strip()
        result=subprocess.run(['git','diff','--name-only',diff_base,'HEAD'],
                              cwd=ROOT,text=True,capture_output=True,check=True)
        changed=result.stdout.splitlines()
        shared=any(x.startswith(('scripts/','schemas/','tests/')) or x in ('package.json',)
                   for x in changed)
        if not shared:
            slugs={p.split('/')[1] for p in changed if p.startswith('decks/') and len(p.split('/'))>=3}
            decks=[p for p in decks if p.name in slugs]
        if not decks:
            print('NO DECK CHANGES: internal planning-only commit, nothing to build.')
            return
    elif not args.all:
        raise ValueError('Specify --deck SLUG, --changed or --all')
    if not decks:raise ValueError('No authored deck specifications found')
    for deck in decks:build(deck)


if __name__=='__main__':
    try:main()
    except (ValueError,subprocess.CalledProcessError) as exc:
        print('PIPELINE FAILED:',exc,file=sys.stderr)
        sys.exit(1)
