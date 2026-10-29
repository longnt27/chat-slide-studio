#!/usr/bin/env python3
"""Render an editable PPTX to PDF and individual slide PNGs with a montage.

Requires LibreOffice on PATH, PyMuPDF and Pillow. Does not verify PowerPoint motion.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

import fitz
from PIL import Image, ImageOps, ImageDraw


def render(args):
    infile = Path(args.deck).resolve()
    if not infile.exists():
        raise FileNotFoundError(infile)
    output = Path(args.out).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if infile.suffix.lower() == '.pdf':
        pdf = output / infile.name
        if infile != pdf:
            shutil.copy2(infile, pdf)
    elif infile.suffix.lower() == '.pptx':
        lo = shutil.which('libreoffice') or shutil.which('soffice')
        if not lo:
            raise RuntimeError('LibreOffice missing: install libreoffice-impress or use the GitHub CI fallback')
        with tempfile.TemporaryDirectory(prefix='slide-render-profile-') as tmp:
            profile = Path(tmp).resolve().as_uri()
            cmd=[lo, '-env:UserInstallation='+profile, '--headless', '--convert-to',
                 'pdf', '--outdir', str(output), str(infile)]
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=False)
            if result.returncode:
                raise RuntimeError('LibreOffice export failed: '+result.stderr[-1800:])
        pdf=output/(infile.stem+'.pdf')
    else:
        raise ValueError('Supported input: PPTX or PDF')
    if not pdf.exists() or pdf.stat().st_size < 1024:
        raise RuntimeError('PDF missing or empty: '+str(pdf))

    previews=[]
    document=fitz.open(pdf)
    pngs=output/'slides'
    pngs.mkdir(exist_ok=True)
    for n,page in enumerate(document,1):
        pix=page.get_pixmap(matrix=fitz.Matrix(args.scale,args.scale),alpha=False)
        filename=pngs/f'slide-{n:02d}.png'
        pix.save(filename)
        previews.append(filename)
    count=len(previews)
    if args.expected is not None and args.expected!=count:
        raise RuntimeError(f'Expected {args.expected} slides, rendered {count}')

    images=[]
    width=round(args.thumb_width)
    for slide_img in previews:
        with Image.open(slide_img) as src:
            image=src.convert('RGB')
            height=round(width/image.width*image.height)
            image.thumbnail((width,height),Image.Resampling.LANCZOS)
            tile=Image.new('RGB',(width,height+34),'#e9edf2')
            tile.paste(image,((width-image.width)//2,0))
            draw=ImageDraw.Draw(tile)
            draw.text((12,height+9),slide_img.stem.replace('-',' ').title(),fill='#263545')
            images.append(tile)
    if images:
        cols=min(max(1,args.columns),len(images))
        rows=(len(images)+cols-1)//cols
        padding=14
        tw,th=images[0].size
        montage=Image.new('RGB',(cols*tw+(cols+1)*padding,rows*th+(rows+1)*padding),'#d7dde5')
        for i,tile in enumerate(images):
            x=padding+(i%cols)*(tw+padding)
            y=padding+(i//cols)*(th+padding)
            montage.paste(tile,(x,y))
        montage.save(output/'montage.png',optimize=True)
    print(f'RENDER PASS: {count} slides -> {output}')
    print('PDF:',pdf)
    print('Montage:',output/'montage.png')
    print('NOTE: static rendering cannot certify Morph/Fade/On Click playback in PowerPoint')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('deck')
    ap.add_argument('--out',required=True)
    ap.add_argument('--expected',type=int)
    ap.add_argument('--scale',type=float,default=1.5)
    ap.add_argument('--thumb-width',type=int,default=460)
    ap.add_argument('--columns',type=int,default=4)
    render(ap.parse_args())
