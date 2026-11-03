#!/usr/bin/env python3
"""Internal storyboard validation, optional legacy HITL locks and production contracts.

New decks create a complete storyboard internally and can build without a user
approval.json. Old approvals remain verifiable when supplied; never fabricate one.
Slide revisions may authorize explicit deviations through revision_requests.json.
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
from presentation_profile import tier_of, motion_of, TIERS, ANIMATION_MODES

ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(plan):
    return hashlib.sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True,
          separators=(',', ':')).encode('utf-8')).hexdigest()


def reveal_sequence(slide,mode='presenter'):
    if mode=='none':
        # Every unit starts visible. There are no entrance effects.
        if slide['type']=='diagram':return ['static','static']+(['static'] if slide.get('bottom') else [])
    
    ty=slide['type']
    if ty=='contents':return ['static']*len(slide.get('entries',[]))
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
    if ty=='contents': return len(slide.get('entries',[]))
    if ty in ('cards','summary'): return len(slide.get('cards',[]))
    if ty=='timeline': return len(slide.get('events',[]))
    if ty in ('split','section'):return len(slide.get('bullets',[]))
    if ty=='comparison': return 2
    if ty=='diagram':return len(slide.get('items',[]))
    return 0


def validate_plan(folder):
    folder=Path(folder)
    path=folder/'storyboard.json'
    if not path.exists():raise ValueError(f'Internal storyboard missing: {path}; plan the full deck before building')
    plan=read(path)
    schema=read(ROOT/'schemas/storyboard.schema.json')
    problems=[f"{'.'.join(map(str,e.absolute_path))}: {e.message}" for e in
              Draft202012Validator(schema).iter_errors(plan)]
    if plan.get('deck_id')!=folder.name:problems.append('storyboard deck_id != deck directory')
    slides=plan.get('slides',[])
    requested=plan.get('requested_slide_count')
    if len(slides)!=requested:problems.append(f'storyboard logical count {len(slides)} != requested {requested}')
    tier=tier_of(plan)
    mode=motion_of(plan)
    if tier not in TIERS or mode not in ANIMATION_MODES:
        problems.append('unknown presentation tier or animation_mode')
    nav=plan.get('navigation')
    if mode=='none' and nav:
        problems.append('hub_return navigation requires presenter animation mode')
    if nav:
        hub=nav.get('hub_slide')
        after=nav.get('return_after',[])
        if not isinstance(hub,int) or not (1<hub<len(slides)) or slides[hub-1].get('layout')!='contents':
            problems.append('navigation hub_slide must refer to a TOC slide')
        if len(after)!=len(set(after)) or not after:
            problems.append('navigation requires unique return_after slides')
        for n in after:
            if not isinstance(n,int) or not (isinstance(hub,int) and hub<n<len(slides)-1):
                problems.append('return_after must be content after TOC and before closing')
        if isinstance(hub,int) and 1<hub<=len(slides) and nav.get('morph'):
            toc=slides[hub-1].get('toc_entries',[])
            ids={e.get('morph_id') for e in toc}
            for entry in toc:
                target=entry.get('target_slide')
                if not isinstance(target,int) or not hub<target<len(slides):
                    problems.append('TOC target_slide must refer to a content slide after the hub')
                elif slides[target-1].get('morph_subject')!=entry.get('morph_id'):
                    problems.append(f'TOC target {target} has no approved matching morph_subject')
            if len(ids)!=len(toc):
                problems.append('TOC Morph requires unique picture subjects')
            route=[]
            for n in range(1,len(slides)+1):
                route.append(n)
                if n in after:route.append(hub)
            for prev,nxt in zip(route,route[1:]):
                if not ((prev==hub and nxt>hub) or (nxt==hub and prev>hub)):continue
                prev_ids=ids if prev==hub else {slides[prev-1].get('morph_subject')}
                next_ids=ids if nxt==hub else {slides[nxt-1].get('morph_subject')}
                if not (prev_ids & next_ids):
                    problems.append(f'Hub Morph needs matched approved visual subject from logical {prev} to {nxt}')
    for i,sl in enumerate(slides,1):
        if sl.get('number')!=i: problems.append(f'storyboard slide number at {i} must be {i}')
        if any('TODO:' in str(sl.get(field,'')) for field in ('title','takeaway','composition','visual')):
            problems.append(f'storyboard slide {i} still contains TODO placeholders; write a real proposed layout')
        seq=sl.get('reveal_sequence',[])
        kind=sl.get('layout')
        units=sl.get('content_units',0)
        if kind=='contents':
            toc=sl.get('toc_entries',[])
            if units!=len(toc) or seq!=['static']*len(toc):
                problems.append(f'storyboard slide {i}: TOC thumbnails must all be static and match content_units')
        if kind=='chart' and (units!=0 or seq or not sl.get('chart_kind')):
            problems.append(f'storyboard slide {i}: chart is one complete visualization with a chart_kind')
        if kind in ('cards','summary','timeline','comparison') and len(seq)!=units:
            problems.append(f'storyboard slide {i}: reveal_sequence needs one entry per content unit')
        if kind in ('cover','thanks','quote') and (units!=0 or seq):
            problems.append(f'storyboard slide {i}: cover/thanks/quote must not have arbitrary card reveal units')
        if kind in ('section','split') and len(seq) not in (units,units+1):
            problems.append(f'storyboard slide {i}: split reveal steps must be bullet count plus optional image step')
        if kind=='diagram' and len(seq) not in (2,3):
            problems.append(f'storyboard slide {i}: diagram needs auto root, peer click, optional bottom click')
        if mode=='none' and any(x!='static' for x in seq):
            problems.append(f'storyboard slide {i}: static tier cannot have entrance animations')
        if mode=='none' and sl.get('morph_from_previous'):
            problems.append(f'storyboard slide {i}: static tier cannot Morph')
        if mode=='presenter' and kind in ('cards','summary','timeline','comparison') and sl.get('content_units',0)>=2:
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


def validate_production_plan(folder, plan=None):
    """Internal plans require no user approval; preserve legacy approval checks."""
    folder = Path(folder)
    plan = plan or validate_plan(folder)
    if (folder / "approval.json").exists():
        return validate_approval(folder, plan)
    return {"approval_channel": "internal", "storyboard_sha256": digest(plan)}


def check_deck_against_plan(folder,plan=None,allowed_slide_changes=None):
    folder=Path(folder)
    plan=plan or validate_plan(folder)
    deckfile=folder/'deck.json'
    if not deckfile.exists():raise ValueError('Internal storyboard exists, but no deck.json has been authored')
    deck=read(deckfile)
    allowed=set(allowed_slide_changes or [])
    problems=[]
    if deck.get('id')!=plan['deck_id']:problems.append('deck id differs from approved storyboard')
    if deck.get('requested_slide_count')!=plan['requested_slide_count']:
        problems.append('slide count differs from approved storyboard')
    if deck.get('title')!=plan['title']:problems.append('deck title differs from approved storyboard')
    if tier_of(deck)!=tier_of(plan):
        problems.append('presentation tier changed after approval')
    if motion_of(deck)!=motion_of(plan):
        problems.append('animation_mode changed after approval')
    if deck.get('navigation')!=plan.get('navigation'):
        problems.append('navigation route changed after approval')
    slides=deck.get('slides',[])
    if len(slides)!=len(plan['slides']):problems.append('slide count differs from approved storyboard')
    planned_morph=[s['number'] for s in plan['slides'] if s.get('morph_from_previous')]
    if sorted(deck.get('morph_to_slides',[]))!=planned_morph:
        problems.append('Morph destinations differ from approved storyboard')
    for idx,(actual,expected) in enumerate(zip(slides,plan['slides']),1):
        if idx in allowed:
            continue  # Revision QA separately verifies the change and its scope.
        if actual['type']!=expected['layout']:problems.append(f'slide {idx} layout changed')
        if actual.get('type')=='contents':
            actual_entries=[{k:v.get(k) for k in ('title','image','morph_id','target_slide')} for v in actual.get('entries',[])]
            if actual_entries!=expected.get('toc_entries',[]):
                problems.append(f'slide {idx} TOC images/targets changed after approval')
        if actual.get('type')=='chart' and actual.get('chart_data',{}).get('kind')!=expected.get('chart_kind'):
            problems.append(f'slide {idx} chart kind changed after approval')
        if expected.get('morph_subject') and actual.get('morph_id')!=expected.get('morph_subject'):
            problems.append(f'slide {idx} Morph subject changed after approval')
        if actual['title']!=expected['title']:problems.append(f'slide {idx} title changed')
        if actual['type']=='diagram':
            approved_relation=expected.get('diagram_relationship','peers')
            authored_relation=actual.get('diagram_relationship','peers')
            if authored_relation!=approved_relation:
                problems.append(f'slide {idx} semantic diagram relationship changed from approved storyboard')
        if content_units(actual)!=expected['content_units']:
            problems.append(f'slide {idx} content unit count changed: {content_units(actual)} vs {expected["content_units"]}')
        if reveal_sequence(actual,motion_of(plan))!=expected['reveal_sequence']:
            problems.append(f'slide {idx} animation sequence changed from approved storyboard')
        if actual.get('type')=='thanks' and expected.get('closing_style','plain')!='creative':
            if actual.get('closing_style','plain')=='creative':problems.append('Unapproved creative closing')
    if problems:raise ValueError('Deck violates internal storyboard + authorized revisions:\n- '+'\n- '.join(problems))
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
    parser.add_argument('--proposals-only',action='store_true',help='Validate internal plans without deck.json')
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
            validate_production_plan(folder,plan)
            from revision_qa import verify
            revised=verify(folder)
            check_deck_against_plan(folder,plan,allowed_slide_changes=revised['authorized_logical_slides'] if revised else None)
        print('INTERNAL PLAN CHECK OK:',folder.name,len(plan['slides']),'slides',('plan only' if args.proposals_only or args.all_proposals else 'build-ready'))

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError) as e:
        print('HITL BLOCKED:',e,file=sys.stderr)
        sys.exit(1)
