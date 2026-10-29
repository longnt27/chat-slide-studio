#!/usr/bin/env python3
"""Download user-approved, attributed public images for a reproducible PPTX build.

Manifest accepts `commons_title` (preferred for Wikimedia), verified `url`, or local_path.
`fallback_urls` are attempted in order. Missing required assets fail in --strict.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image

COMMONS = 'https://commons.wikimedia.org/w/api.php'
USER_AGENT = 'ProfessionalPresentationBuilder/1.0 (+https://github.com/)'
SUPPORTED = {'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}


def download(url, retries=3):
    scheme=urllib.parse.urlsplit(url).scheme.lower()
    if scheme not in ('http','https'):
        raise ValueError('Only HTTP(S) sources allowed: '+url)
    last=None
    for attempt in range(retries):
        try:
            request=urllib.request.Request(url,headers={
                'User-Agent':USER_AGENT,'Accept':'image/*,application/json;q=0.9,*/*;q=0.7'})
            with urllib.request.urlopen(request,timeout=30) as resp:
                data=resp.read(25_000_001)
                if len(data)>25_000_000: raise ValueError('Image exceeds 25MB per asset')
                if len(data)<128: raise ValueError('Image or API response too small')
                return data
        except Exception as exc:
            last=exc
            time.sleep(min(2*(attempt+1),6))
    raise RuntimeError(f'{url}: {last}')


def no_html(text):
    return re.sub(r'<[^>]+>','',html.unescape(text or '')).strip()


def commons_info(title):
    params=urllib.parse.urlencode({'action':'query','format':'json','prop':'imageinfo',
        'iiprop':'url|extmetadata','iiurlwidth':1800,'titles':'File:'+title})
    raw=download(COMMONS+'?'+params)
    result=json.loads(raw)
    entries=list(result.get('query',{}).get('pages',{}).values())
    if not entries or 'imageinfo' not in entries[0]:
        raise ValueError('Commons image not found: '+title)
    info=entries[0]['imageinfo'][0]
    metadata=info.get('extmetadata',{})
    def m(key): return no_html(metadata.get(key,{}).get('value',''))
    url='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(title.replace(' ','_'))
    return {'download_url':info.get('thumburl') or info['url'],
      'source_page':url,'author':m('Artist'),'license':m('LicenseShortName'),
      'license_url':m('LicenseUrl')}


def image_dimensions(data):
    from io import BytesIO
    with Image.open(BytesIO(data)) as im:
        ext=SUPPORTED.get(im.format)
        if not ext: raise ValueError('Unsupported raster image: '+str(im.format))
        w,h=im.size
        if w<120 or h<120: raise ValueError(f'Image too small: {w}x{h}')
        im.verify()
    return ext,w,h


def run(manifest_file,out,strict=False):
    entries=json.loads(Path(manifest_file).read_text(encoding='utf-8')).get('assets',[])
    if not entries:raise ValueError('Image manifest is empty')
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    rows=[]; errors=[]; observed_ids=set()
    for a in entries:
        aid=a.get('id','').strip()
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',aid) or aid in observed_ids:
            raise ValueError('Unsafe/duplicate asset id: '+repr(aid))
        observed_ids.add(aid)
        source={'download_url':a.get('url'),
                'source_page':a.get('source_page',''),
                'author':a.get('author',''),
                'license':a.get('license',''),
                'license_url':a.get('license_url','')}
        data=None
        if a.get('local_path'):
            root=Path(manifest_file).resolve().parent
            local=(root/a['local_path']).resolve()
            if not local.is_relative_to(root):
                raise ValueError('Asset escapes deck directory: '+aid)
            data=local.read_bytes()
            ext,w,h=image_dimensions(data)
            source['download_url']='local:'+a['local_path']
        else:
            if a.get('commons_title'):
                try:source={**commons_info(a['commons_title']),**{k:v for k,v in source.items() if v}}
                except Exception as exc:
                    print('WARN metadata for',aid,exc,file=sys.stderr)
            urls=[source.get('download_url')]+a.get('fallback_urls',[])
            for target in filter(None,urls):
                try:
                    data=download(target)
                    ext,w,h=image_dimensions(data)
                    source['download_url']=target
                    break
                except Exception as exc:
                    print('WARN',aid,exc,file=sys.stderr)
        if data is None:
            issue=f'Asset {aid}: cannot download a validated raster image'
            if a.get('required',True):errors.append(issue)
            else:print('OPTIONAL:',issue,file=sys.stderr)
            continue
        digest=hashlib.sha256(data).hexdigest()
        expected=a.get('sha256')
        if expected and expected.lower()!=digest:
            errors.append(f'Asset {aid}: checksum mismatch')
            continue
        author=source.get('author','').strip()
        license_=source.get('license','').strip()
        source_page=source.get('source_page','').strip()
        if strict and any((not x or x.lower().startswith(('fill in','unknown','see source')))
                          for x in [author,license_,source_page]):
            errors.append(f'Asset {aid}: missing verified author/license/source_page')
            continue
        file=out/(aid+ext)
        file.write_bytes(data)
        row={'id':aid,'path':str(file.resolve()),'filename':file.name,
             'subject':a.get('subject',''),'author':author,'license':license_,
             'license_url':source.get('license_url',''),
             'source_page':source_page,'download_url':source['download_url'],
             'sha256':digest,'width':w,'height':h}
        rows.append(row)
        print(f'ASSET {aid}: {w}x{h} {len(data)//1024}KB sha256:{digest[:12]}')
    columns=['id','filename','subject','author','license','license_url','source_page','download_url','sha256','width','height']
    with (out/'credits.csv').open('w',encoding='utf-8',newline='') as fp:
        writer=csv.DictWriter(fp,fieldnames=columns,extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
    (out/'assets.json').write_text(json.dumps({'assets':rows,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
    if errors:
        print('ASSET ISSUES:',*errors,sep='\n  ',file=sys.stderr)
    if strict and errors: return 1
    print('ASSETS:',len(rows),'fetched; metadata:',out/'credits.csv')
    return 0


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest')
    p.add_argument('--out',required=True)
    p.add_argument('--strict',action='store_true')
    args=p.parse_args()
    sys.exit(run(args.manifest,args.out,args.strict))
