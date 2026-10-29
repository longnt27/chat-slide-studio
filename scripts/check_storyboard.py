#!/usr/bin/env python3
"""HITL gate. A chatbot must obtain explicit user approval of a visual storyboard
before writing deck.json. CI locks layout/order/click plan to the approved version.

The digest proves that the reviewed plan was not changed. It DOES NOT itself
prove that a chat message came from a human; the ChatGPT agent must faithfully
record the actual approving turn, and must never fabricate an approval.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(plan):
    return hashlib.sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True,
          separators=(',', ':')).encode('utf-8')).hexdigest()


def reveal_sequence(slide):
    ty=slide['type']
    if ty in ('cards','summary'):
        entries=slide.get('cards',[])
        return [item.get('reveal') or ('auto' if i==0 else 'click')
                for i,item in enumerate(entries)]
    if ty=='timeline':
        return [item.get('reveal') or ('auto' if i==0 else 'click')
                for i,item in enumerate(slide.get('events',[]))]
    if ty in ('section','split'):
        out=[]
        if slide.get('image') and not slide.get('morph_id'):
            out.append(slide.get('image_reveal') or 'auto')
        out.extend(item.get('reveal') or ('auto' if i==0 else 'click')
                   for i,item in enumerate(slide.get('bullets',[])))
        return out
    if ty=='comparison':
        return [slide[key].get('reveal') or ('auto' if index==0 else 'click')
                for index,key in enumerate(('left','right'))]
    if ty=='diagram':
        return ['auto','click']+(['click'] if slide.get('bottom') else [])
    return []


def content_units(slide):
    ty=slide['type']
    if ty in ('cards','summary'): return len(slide.get('cards',[]))
    if ty=='timeline': return len(slide.get('events',[]))
    if ty in ('split','section'):return len(slide.get('bullets',[]))
    if ty=='comparison': return 2
    if ty=='diagram':return len(slide.get('items',[]))
    return 0


def validate_plan(folder):
    folder=Path(folder)
    path=folder/'storyboard.json'
    if not path.exists():raise ValueError(f'HITL plan missing: {path}; propose slide-by-slide layouts first')
    plan=read(path)
    schema=read(ROOT/'schemas/storyboard.schema.json')
    problems=[f"{'.'.join(map(str,e.absolute_path))}: {e.message}" for e in
              Draft202012Validator(schema).iter_errors(plan)]
    if plan.get('deck_id')!=folder.name:problems.append('storyboard deck_id != deck directory')
    slides=plan.get('slides',[])
    requested=plan.get('requested_slide_count')
    if len(slides)!=requested:problems.append(f'storyboard count {len(slides)} != requested {requested}')
    for i,sl in enumerate(slides,1):
        if sl.get('number')!=i: problems.append(f'storyboard slide number at {i} must be {i}')
        if any('TODO:' in str(sl.get(field,'')) for field in ('title','takeaway','composition','visual')):
            problems.append(f'storyboard slide {i} still contains TODO placeholders; write a real proposed layout')
        seq=sl.get('reveal_sequence',[])
        kind=sl.get('layout')
        units=sl.get('content_units',0)
        if kind in ('cards','summary','timeline','comparison') and len(seq)!=units:
            problems.append(f'storyboard slide {i}: reveal_sequence needs one entry per content unit')
        if kind in ('cover','thanks','quote') and (units!=0 or seq):
            problems.append(f'storyboard slide {i}: cover/thanks/quote must not have arbitrary card reveal units')
        if kind in ('section','split') and len(seq) not in (units,units+1):
            problems.append(f'storyboard slide {i}: split reveal steps must be bullet count plus optional image step')
        if kind=='diagram' and len(seq) not in (2,3):
            problems.append(f'storyboard slide {i}: diagram needs auto root, peer click, optional bottom click')
        if kind in ('cards','summary','timeline','comparison') and sl.get('content_units',0)>=2:
            if 'click' not in seq and len(sl.get('no_animation_reason',''))<16:
                problems.append(f'storyboard slide {i}: multiple items require presenter On Click steps (or explicitly justified static layout)')
        if 'click' in seq and any(v=='static' for v in seq[seq.index('click')+1:]):
            problems.append(f'storyboard slide {i}: later units cannot be static after hidden on-click units')
        morph=sl.get('morph_from_previous')
        if morph and i==1:problems.append('cover cannot Morph from previous')
        if morph and len(sl.get('morph_reason','').strip())<24:
            problems.append(f'storyboard slide {i} Morph needs a meaningful subject + geometry explanation')
        if sl.get('layout')=='thanks' and sl.get('closing_style','plain')=='creative' and not sl.get('takeaway'):
            problems.append('creative closing must be intentionally articulated')
    if problems:raise ValueError('Storyboard validation failed:\n- '+'\n- '.join(problems))
    return plan


def validate_approval(folder,plan=None):
    folder=Path(folder)
    plan=plan or validate_plan(folder)
    path=folder/'approval.json'
    if not path.exists():raise ValueError('HITL approval missing: present storyboard to user and STOP before writing deck.json')
    approval=read(path)
    if approval.get('status')!='approved':raise ValueError('HITL status is not approved')
    if approval.get('storyboard_sha256')!=digest(plan):
        raise ValueError('HITL storyboard changed after approval; request human re-approval')
    if approval.get('deck_id')!=folder.name:
        raise ValueError('HITL approved deck_id mismatch')
    if approval.get('approval_channel') not in ('chat','github_review','demo_fixture'):
        raise ValueError('HITL approval_channel must be chat, github_review or demo_fixture')
    if approval['approval_channel']=='demo_fixture' and folder.name!='demo':
        raise ValueError('demo_fixture approval is forbidden for production decks')
    if approval['approval_channel']!='demo_fixture':
        if approval.get('approved_by')!='user':
            raise ValueError('HITL needs explicit approval by user')
        if len(approval.get('approval_quote','').strip())<2:
            raise ValueError('HITL approval_quote missing: do not invent user consent')
    return approval


def check_deck_against_plan(folder,plan=None):
    folder=Path(folder)
    plan=plan or validate_plan(folder)
    deckfile=folder/'deck.json'
    if not deckfile.exists():raise ValueError('Approved storyboard exists, but no deck.json has been authored')
    deck=read(deckfile)
    problems=[]
    if deck.get('id')!=plan['deck_id']:problems.append('deck id differs from approved storyboard')
    if deck.get('requested_slide_count')!=plan['requested_slide_count']:
        problems.append('slide count differs from approved storyboard')
    if deck.get('title')!=plan['title']:problems.append('deck title differs from approved storyboard')
    slides=deck.get('slides',[])
    if len(slides)!=len(plan['slides']):problems.append('slide count differs from approved storyboard')
    planned_morph=[s['number'] for s in plan['slides'] if s.get('morph_from_previous')]
    if sorted(deck.get('morph_to_slides',[]))!=planned_morph:
        problems.append('Morph destinations differ from approved storyboard')
    for idx,(actual,expected) in enumerate(zip(slides,plan['slides']),1):
        if actual['type']!=expected['layout']:problems.append(f'slide {idx} layout changed')
        if actual['title']!=expected['title']:problems.append(f'slide {idx} title changed')
        if actual['type']=='diagram':
            approved_relation=expected.get('diagram_relationship','peers')
            authored_relation=actual.get('diagram_relationship','peers')
            if authored_relation!=approved_relation:
                problems.append(f'slide {idx} semantic diagram relationship changed from approved storyboard')
        if content_units(actual)!=expected['content_units']:
            problems.append(f'slide {idx} content unit count changed: {content_units(actual)} vs {expected["content_units"]}')
        if reveal_sequence(actual)!=expected['reveal_sequence']:
            problems.append(f'slide {idx} animation sequence changed from approved storyboard')
        if actual.get('type')=='thanks' and expected.get('closing_style','plain')!='creative':
            if actual.get('closing_style','plain')=='creative':problems.append('Unapproved creative closing')
    if problems:raise ValueError('Deck violates approved HITL storyboard:\n- '+'\n- '.join(problems))
    return True


def approve(folder,quote,channel='chat'):
    """Only invoke this after actually receiving the user's approval in chat.
    This helper merely locks the plan hash; it cannot verify human identity.
    """
    if channel not in ('chat','github_review'):raise ValueError('Invalid approval channel')
    if not quote or len(quote.strip())<2:raise ValueError('Explicit approval quote required')
    folder=Path(folder)
    plan=validate_plan(folder)
    approval={
      'deck_id':folder.name,'status':'approved','approved_by':'user',
      'approval_channel':channel,'approval_quote':quote.strip(),
      'approved_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
      'storyboard_sha256':digest(plan)
    }
    (folder/'approval.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return approval


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path,nargs='?',help='decks/<slug> folder')
    parser.add_argument('--proposals-only',action='store_true',help='Validate proposed plans without approval or deck.json')
    parser.add_argument('--all-proposals',action='store_true',help='Check all storyboard files; no deck build')
    parser.add_argument('--approve-quoted',default='',help='Quote actual user approval, ONLY after the user has approved in chat')
    parser.add_argument('--channel',default='chat',choices=['chat','github_review'])
    args=parser.parse_args()
    if args.all_proposals:
        folders=sorted(p.parent for p in (ROOT/'decks').glob('*/storyboard.json'))
    else:
        if not args.folder:parser.error('folder or --all-proposals required')
        folders=[args.folder]
    for folder in folders:
        plan=validate_plan(folder)
        if args.approve_quoted:
            a=approve(folder,args.approve_quoted,args.channel)
            print('LOCKED HITL PLAN',folder.name,a['storyboard_sha256'])
        elif not(args.proposals_only or args.all_proposals):
            validate_approval(folder,plan)
            check_deck_against_plan(folder,plan)
        print('HITL CHECK OK:',folder.name,len(plan['slides']),'slides',('proposal only' if args.proposals_only or args.all_proposals else 'approved'))

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError) as e:
        print('HITL BLOCKED:',e,file=sys.stderr)
        sys.exit(1)
