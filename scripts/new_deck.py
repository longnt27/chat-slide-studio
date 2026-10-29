#!/usr/bin/env python3
"""Create a HITL storyboard first, and a PPTX specification only after approval.

The default invocation intentionally NEVER writes deck.json. ChatGPT proposes the
wireframes, gets explicit user consent in chat, records the immutable plan hash,
then calls --from-approved-plan to generate the deck skeleton for authorship.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from check_storyboard import validate_plan, validate_approval

ROOT=Path(__file__).resolve().parent.parent


def new_deck(slug,title,slides=15,root=ROOT,from_approved_plan=False):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,55}',slug):
        raise ValueError('Deck slug: 2-56 lowercase alphanumeric/hyphen characters')
    if slides<1 or slides>80 or slides==2:
        raise ValueError('Slides: 1 standalone or 3-80 for complete presentation')
    folder=root/'decks'/slug
    if from_approved_plan:
        plan=validate_plan(folder)
        validate_approval(folder,plan)
        if (folder/'deck.json').exists():raise ValueError('deck.json already exists; do not overwrite')
        assembled=[]
        for sl in plan['slides']:
            ty=sl['layout'];n=sl['content_units']
            item={'type':ty,'title':sl['title'],
                  'subtitle':'TODO: write final fact-based slide subtitle',
                  'notes':'TODO: write a full speaker script and verified sources.'}
            if ty in ('cards','summary'):
                item['cards']=[{'title':f'TODO: content unit {i+1}','text':'TODO: evidence and explanation',
                                'reveal':rv} for i,rv in enumerate(sl['reveal_sequence'])]
            elif ty=='timeline':
                item['events']=[{'title':f'TODO: event {i+1}','text':'TODO: date and evidence',
                                'reveal':rv} for i,rv in enumerate(sl['reveal_sequence'])]
            elif ty in ('split','section'):
                # The approved animation plan may include a separate photo reveal.
                plan_reveal=list(sl['reveal_sequence'])
                if n==0:plan_reveal=[]
                elif len(plan_reveal)>n:plan_reveal=plan_reveal[-n:]
                item['bullets']=[{'title':f'TODO: point {i+1}','text':'TODO: body and explanation',
                                  'reveal':rv} for i,rv in enumerate(plan_reveal)]
            elif ty=='comparison':
                item['left']={'title':'TODO: left evidence','text':'TODO: facts','reveal':sl['reveal_sequence'][0]}
                item['right']={'title':'TODO: right evidence','text':'TODO: facts','reveal':sl['reveal_sequence'][1]}
            elif ty=='diagram':
                item['root']='TODO: root';item['group_label']='TODO: heading';
                item['items']=[f'TODO: concept {i+1}' for i in range(n)]
                if len(sl['reveal_sequence'])==3:item['bottom']='TODO: synthesis'
            elif ty=='quote':
                item['quote']='TODO: attributed quote';item['attribution']='TODO: verified author'
            if ty=='thanks':
                item['closing_style']=sl.get('closing_style','plain')
                item['subtitle']='Cảm ơn đã lắng nghe. Mời đặt câu hỏi.'
            assembled.append(item)
        result={'id':slug,'title':plan['title'],'language':'vi',
                'requested_slide_count':plan['requested_slide_count'],
                'theme':{'preset':'modern'},
                'morph_to_slides':[s['number'] for s in plan['slides'] if s['morph_from_previous']],
                'slides':assembled}
        (folder/'deck.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if not (folder/'sources.json').exists():
            (folder/'sources.json').write_text('{"assets": []}\n')
        print(f'Created POST-APPROVAL deck skeleton: {len(assembled)} slides at {folder}/deck.json')
        return folder
    folder.mkdir(parents=True,exist_ok=False)
    slides_out=[]
    for number in range(1,slides+1):
        layout='cover' if number==1 else ('thanks' if number==slides else 'section')
        slides_out.append({'number':number,'layout':layout,
           'title':title if number==1 else ('CẢM ƠN' if layout=='thanks' else f'TODO: slide {number} title'),
           'takeaway':'TODO: precise message the audience should remember',
           'composition':'TODO: columns, visual hierarchy and text/image zones',
           'visual':'TODO: photo, map, diagram or factual material to show',
           'content_units':0,'reveal_sequence':[],
           'morph_from_previous':False,
           **({'closing_style':'plain'} if layout=='thanks' else {})})
    plan={'deck_id':slug,'title':title,'requested_slide_count':slides,'slides':slides_out}
    (folder/'storyboard.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'sources.json').write_text('{"assets": []}\n',encoding='utf-8')
    print(f'Created proposal ONLY: {folder}/storyboard.json, {slides} layout entries. NO deck.json until approval.')
    return folder


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('slug');p.add_argument('--title')
    p.add_argument('--slides',type=int,default=15)
    p.add_argument('--from-approved-plan',action='store_true')
    a=p.parse_args()
    if not a.from_approved_plan and not a.title:p.error('--title required for new proposal')
    new_deck(a.slug,a.title or '',a.slides,from_approved_plan=a.from_approved_plan)
