#!/usr/bin/env python3
"""Create a specified-length deck scaffold that ChatGPT must fill before delivery.

A 15-slide request starts with 15 placeholder slides, never a three-slide file
that happens to pass a PPTX smoke test. `TODO:` is rejected by check_spec.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent


def new_deck(slug: str, title: str, slides: int = 15, root: Path = ROOT):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,55}',slug):
        raise ValueError('Deck slug: 2-56 lowercase alphanumeric/hyphen characters')
    if slides < 1 or slides > 80 or slides == 2:
        raise ValueError('Slides: 1 for a standalone slide, or 3-80 for a complete presentation')
    folder=root/'decks'/slug
    folder.mkdir(parents=True,exist_ok=False)
    content=[]
    content.append({
        'type':'cover',
        'eyebrow':'CHUYEN DE',
        'title':title,
        'subtitle':'TODO: Write the real opening thesis and audience promise.',
        'notes':'TODO: Introduce the speaker, topic, audience and why it matters.'
    })
    for n in range(2,slides):
        # Keep the scaffold lightweight and editable. The agent should choose
        # the best layout for the actual subject before the first commit.
        content.append({
            'type':'section',
            'eyebrow':f'{n-1:02d} / NOI DUNG',
            'title':f'TODO: Slide {n} thesis',
            'subtitle':'TODO: Add a meaningful proof point, example, or visual.',
            'notes':'TODO: Write what the presenter says here and where to click next.'
        })
    if slides > 1:
        content.append({
            'type':'thanks',
            'eyebrow':'KET THUC',
            'title':'CAM ON',
            'subtitle':'TODO: Wrap up with a concise memorable closing.',
            'notes':'TODO: Summarize the main takeaways and invite questions.'
        })
    deck={
        'id':slug,
        'title':title,
        'language':'vi',
        'requested_slide_count':slides,
        'theme':{'preset':'modern'},
        'morph_to_slides':[],
        'slides':content
    }
    (folder/'deck.json').write_text(json.dumps(deck,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (folder/'sources.json').write_text('{"assets": []}\n',encoding='utf8')
    print(f'Created {folder}: {slides} placeholder slide(s). Replace every TODO before CI.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('slug')
    p.add_argument('--title',required=True)
    p.add_argument('--slides',required=False,type=int,default=15)
    a=p.parse_args()
    new_deck(a.slug,a.title,slides=a.slides)
