#!/usr/bin/env python3
"""Presentation tiers, logical slides and expanded physical slideshow route.

A repeat visit to the same table-of-contents slide is one logical slide but
another physical PPTX page. The PPTX/PDF must preserve that expanded sequence.
Pure functions here are shared by schema QA, builder setup and regression tests.
"""
from __future__ import annotations
import json
from pathlib import Path

TIERS=('content','presenter','studio')
ANIMATION_MODES=('none','presenter')


def tier_of(obj):
    # Backwards compatibility: old decks were presenter/animated by default.
    return obj.get('tier','presenter')


def motion_of(obj):
    return obj.get('animation_mode','none' if tier_of(obj)=='content' else 'presenter')


def morph_subjects(slide):
    """One asset and one semantic identifier are required for any Morph pair."""
    pairs=[]
    if slide.get('image') and slide.get('morph_id'):
        pairs.append((slide['morph_id'],slide['image']))
    for field in ('cards','events','bullets','entries'):
        for item in slide.get(field,[]):
            if item.get('morph_id') and item.get('image'):
                pairs.append((item['morph_id'],item['image']))
    return set(pairs)


def compile_route(deck):
    slides=deck.get('slides',[])
    count=len(slides)
    if count!=deck.get('requested_slide_count'):
        raise ValueError('logical slide count must equal requested_slide_count')
    tier=tier_of(deck)
    mode=motion_of(deck)
    if tier not in TIERS:raise ValueError(f'unsupported tier: {tier}')
    if mode not in ANIMATION_MODES:raise ValueError('unknown animation_mode')
    if mode=='none' and deck.get('morph_to_slides'):
        raise ValueError('static deck cannot contain Morph destinations')
    nav=deck.get('navigation')
    hub=returns=set()
    if nav:
        if nav.get('mode')!='hub_return':
            raise ValueError('unsupported navigation mode')
        if mode=='none':
            raise ValueError('hub_return requires presenter motion; choose presenter/studio')
        hub=nav['hub_slide']
        if not isinstance(hub,int) or isinstance(hub,bool) or not 1<hub<count:
            raise ValueError('hub_slide must be an interior logical slide')
        if slides[hub-1].get('type')!='contents':
            raise ValueError('hub_slide must be a contents slide')
        returns=nav['return_after']
        if not returns or len(returns)!=len(set(returns)):
            raise ValueError('return_after must have unique slide numbers')
        for n in returns:
            if not isinstance(n,int) or n<=hub or n>=count-1:
                raise ValueError('return_after must be a content slide after hub, before the closing slide')
            if slides[n-1]['type'] in ('contents','cover','thanks'):
                raise ValueError('return_after must point to an ordinary content slide')
        toc=slides[hub-1].get('entries',[])
        if len(toc)<2:
            raise ValueError('navigation hub requires at least two TOC entries')
        targets=[v.get('target_slide') for v in toc]
        if len(set(targets))!=len(targets):
            raise ValueError('TOC target_slide values must be unique')
        for target in targets:
            if not isinstance(target,int) or not (hub<target<count):
                raise ValueError('TOC entries must target content slides after the hub')
        if nav.get('morph',False):
            if not all(x.get('image') and x.get('morph_id') for x in toc):
                raise ValueError('Morph TOC requires an image and unique morph_id on every entry')
            if len({x['morph_id'] for x in toc}) != len(toc):
                raise ValueError('Morph TOC needs unique subject identifiers')
    sequence=[]
    for index in range(1,count+1):
        sequence.append({'physical':len(sequence)+1,'logical':index,'role':'primary'})
        if nav and index in returns:
            sequence.append({'physical':len(sequence)+1,'logical':hub,'role':'hub_return',
                             'after_logical':index})
    morph=[]
    explicit=set(deck.get('morph_to_slides',[]))
    for n in explicit:
        if not isinstance(n,int) or n<=1 or n>count:
            raise ValueError(f'invalid logical Morph destination {n}')
    for i in range(1,len(sequence)):
        previous,current=sequence[i-1],sequence[i]
        p,c=previous['logical'],current['logical']
        crosshub=bool(nav and nav.get('morph',False) and ((p==hub and c>hub) or (c==hub and p>hub)))
        requested_regular=(current['role']=='primary' and c in explicit and p==c-1)
        if not (crosshub or requested_regular):
            continue
        shared=morph_subjects(slides[p-1])&morph_subjects(slides[c-1])
        if shared:
            morph.append(current['physical'])
        else:
            if crosshub:
                raise ValueError(f'Hub Morph lacks a matching photo+subject between physical slides {i} and {i+1}; review images in storyboard')
            raise ValueError(f'Morph needs the same asset and subject between logical slides {p} and {c}')
    # Count the story in the author's logical slide numbering. The physical deck
    # includes all required revisits so presentation mode has real transitions.
    return {'tier':tier,'animation_mode':mode,
            'logical_count':count,'physical_count':len(sequence),
            'revisit_count':len(sequence)-count,'physical_slides':sequence,
            'morph_physical_destinations':sorted(set(morph)),
            'navigation':nav or None}


def write_route(deck_path):
    deck_path=Path(deck_path)
    deck=json.loads(deck_path.read_text(encoding='utf-8'))
    result=compile_route(deck)
    out=deck_path.parent/'dist'
    out.mkdir(exist_ok=True)
    (out/'slide-route.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('deck_json',type=Path)
    args=p.parse_args()
    route=write_route(args.deck_json)
    print('ROUTE PASS',route['logical_count'],'logical',
          route['physical_count'],'physical',
          route['revisit_count'],'TOC revisits',
          len(route['morph_physical_destinations']),'Morph')
