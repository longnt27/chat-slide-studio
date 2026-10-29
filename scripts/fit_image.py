#!/usr/bin/env python3
"""Fit an image to a 16:9 or other frame without arbitrarily cutting subjects.

Default contains the original image. Cover is allowed only with --decorative.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def fit_image(source, output, width, height, mode='contain',decorative=False,
              background='blur', background_color='#0c2530',meta=None):
    source=Path(source)
    output=Path(output)
    if mode=='cover' and not decorative:
        raise ValueError('Cover cropping forbidden without --decorative; use contain for portraits/documents')
    with Image.open(source) as original:
        original=ImageOps.exif_transpose(original).convert('RGB')
    sw,sh=original.size
    mismatch=max((sw/sh)/(width/height),(width/height)/(sw/sh))
    if mode=='contain':
        if background=='blur':
            bg=ImageOps.fit(original,(width,height),method=Image.Resampling.LANCZOS)
            bg=bg.filter(ImageFilter.GaussianBlur(max(10,int(min(width,height)*.035))))
            bg=ImageEnhance.Brightness(bg).enhance(.35)
            bg=ImageEnhance.Color(bg).enhance(.65)
        else:
            bg=Image.new('RGB',(width,height),background_color)
        inset=max(0,int(min(width,height)*.02))
        full=ImageOps.contain(original,(width-2*inset,height-2*inset),method=Image.Resampling.LANCZOS)
        bg.paste(full,((width-full.width)//2,(height-full.height)//2))
        image=bg
    else:
        image=ImageOps.fit(original,(width,height),method=Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True,exist_ok=True)
    image.save(output,quality=91,optimize=True)
    audit={'source':str(source),'output':str(output),'source_dims':[sw,sh],
           'output_dims':[width,height],'mode':mode,'decorative':decorative,
           'aspect_mismatch':round(mismatch,4),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    if meta:
        Path(meta).write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    return audit


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source')
    ap.add_argument('output')
    ap.add_argument('--width',type=int,required=True)
    ap.add_argument('--height',type=int,required=True)
    ap.add_argument('--mode',choices=['contain','cover'],default='contain')
    ap.add_argument('--decorative',action='store_true')
    ap.add_argument('--background',choices=['blur','solid'],default='blur')
    ap.add_argument('--background-color',default='#0c2530')
    ap.add_argument('--meta')
    args=ap.parse_args()
    print(json.dumps(fit_image(args.source,args.output,args.width,args.height,
          args.mode,args.decorative,args.background,args.background_color,args.meta),indent=2))
