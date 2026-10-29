#!/usr/bin/env python3
"""Render 16:9 composition *wireframes* before HITL approval, not final slides.

This is intentionally a neutral layout sketch with card positions, image slots,
click stages, and Morph intentions. The user approves it in CHAT; no PPTX is made.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import textwrap
from PIL import Image,ImageDraw,ImageFont
from check_storyboard import validate_plan

FONTS=[('/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'),
       ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
FONT, BOLD=next(((a,b) for a,b in FONTS if Path(a).exists()),FONTS[-1])

def font(size,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,size)

def draw_text(d,text,xy,max_chars,size=18,fill=(233,241,246),bold=False,lines=2):
    x,y=xy
    wrap=textwrap.wrap(str(text),width=max_chars,break_long_words=False,break_on_hyphens=False)
    for idx,line in enumerate(wrap[:lines]):
        d.text((x,y+idx*(size+8)),line,font=font(size,bold),fill=fill)

def cell(d,rect,label,color=(45,68,83),border=(90,130,148)):
    d.rounded_rectangle(rect, radius=8,fill=color,outline=border,width=2)
    draw_text(d,label,(rect[0]+14,rect[1]+14),36,17)

def single(slide):
    w,h=960,540
    im=Image.new('RGB',(w,h),(13,30,43));d=ImageDraw.Draw(im)
    d.rectangle((0,0,w,8),fill=(202,168,110))
    draw_text(d,f"{slide['number']:02d} / {slide['layout'].upper()}",(42,29),44,16,(230,186,112),True)
    draw_text(d,slide['title'],(42,73),56,29,(252,248,235),True)
    draw_text(d,slide['takeaway'],(42,127),84,17,(194,213,222),lines=2)
    left,right,top,bottom=42,918,195,432
    typ=slide['layout'];count=slide['content_units']
    if typ in ('cards','summary','timeline'):
        nc=max(1,count);gap=18;cw=(right-left-gap*(nc-1))/nc
        for i in range(nc):
            x=left+i*(cw+gap)
            cell(d,(x,top,x+cw,bottom),f'Content block {i+1} / {slide["reveal_sequence"][i] if i<len(slide["reveal_sequence"]) else "static"}')
    elif typ in ('section','split','quote'):
        cell(d,(left,top,left+416,bottom),'IMAGE / DIAGRAM / EVIDENCE',color=(46,82,91))
        cell(d,(left+434,top,right,bottom),f'ARGUMENT + {count} CONTENT UNITS')
    elif typ=='diagram':
        cell(d,(320,top,650,top+54),'CENTRAL CLAIM',color=(83,70,48))
        cols=3;smallGap=14
        for i in range(count):
            x=left+(i%cols)*((right-left+smallGap)/cols)
            y=top+80+(i//cols)*61
            cell(d,(x,y,x+273,y+48),f'Node {i+1}')
    elif typ=='comparison':
        cell(d,(left,top,470,bottom),'LEFT ARGUMENT / AUTO')
        cell(d,(490,top,right,bottom),'RIGHT ARGUMENT / CLICK 1')
    elif typ in ('cover','thanks'):
        draw_text(d,'COVER / CLOSE: SINGLE FOCAL HIERARCHY',(144,269),60,26,(224,196,149),True)
    else:
        cell(d,(left,top,right,bottom),'MAIN VISUAL AND MESSAGE')
    d.text((42,449),'IMAGE: '+slide['visual'][:110],font=font(14),fill=(190,211,219))
    clicks=slide['reveal_sequence'].count('click')
    morph='MORPH from previous' if slide['morph_from_previous'] else 'Fade transition'
    d.text((42,481),f'{clicks} presenter clicks  |  {morph}',font=font(15),fill=(225,185,121))
    d.text((920,508),f"{slide['number']:02d}",anchor='ra',font=font(15),fill=(175,189,191))
    return im

def render(folder,out):
    plan=validate_plan(folder)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    thumbs=[]
    for s in plan['slides']:
        img=single(s)
        img.save(out/f"slide-{s['number']:02d}.png")
        img.thumbnail((576,324))
        thumbs.append(img)
    cols=3;rows=(len(thumbs)+cols-1)//cols
    contact=Image.new('RGB',(cols*576+(cols+1)*15,rows*324+(rows+1)*15),(240,240,238))
    for index,im in enumerate(thumbs):
        x=15+(index%cols)*(576+15);y=15+(index//cols)*(324+15)
        contact.paste(im,(x,y))
    contact.save(out/'storyboard-montage.png')
    print('STORYBOARD PREVIEW',len(thumbs),'slides ->',out/'storyboard-montage.png')

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('deck_folder',type=Path)
    ap.add_argument('--out',type=Path)
    a=ap.parse_args()
    render(a.deck_folder,a.out or (a.deck_folder/'storyboard-preview'))
