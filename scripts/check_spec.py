#!/usr/bin/env python3
"""Reject incomplete/unsafe PPTX specifications before expensive CI work.

This validates structure; it cannot fact-check claims or judge image semantics.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
BAD_CAPTIONS = (
    "không phải ảnh chiến sự", "không phải ảnh chụp thời", "not an actual photo of",
    "obviously not", "chỉ là hình minh họa", "just an illustration",
)


def assets_from_slide(slide):
    refs=[]
    if slide.get("image"):
        refs.append((slide["image"], slide.get("morph_id")))
    for key in ("cards", "events", "bullets"):
        for item in slide.get(key, []):
            if item.get("image"):
                refs.append((item["image"], item.get("morph_id")))
    return refs


def validate(specfile: Path):
    specfile=specfile.resolve()
    data=json.loads(specfile.read_text(encoding="utf8"))
    schema=json.loads((ROOT / "schemas/deck.schema.json").read_text(encoding="utf8"))
    errors=[f"schema: {'/'.join(map(str,e.absolute_path))}: {e.message}" for e in
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data)]
    slides=data.get("slides",[])
    requested=data.get('requested_slide_count')
    if isinstance(requested,int) and not isinstance(requested,bool) and len(slides)!=requested:
        errors.append(f"slide_count_mismatch: user requested {requested}, spec contains {len(slides)} slides")
    manifest_path=specfile.parent / "sources.json"
    if not manifest_path.exists():
        errors.append("missing sources.json (use {\"assets\": []} for a text-only deck)")
        sources=[]
    else:
        sources=json.loads(manifest_path.read_text(encoding="utf8")).get("assets",[])
    source_ids=[i.get("id") for i in sources]
    dup=[x for x,c in Counter(source_ids).items() if c>1]
    if dup:errors.append(f"duplicate asset ids: {dup}")
    available=set(source_ids)
    if slides:
        if slides[0].get('type')!='cover':errors.append("first slide must be cover")
        if len(slides)>1 and slides[-1].get('type')!='thanks':
            errors.append("last slide must be thanks")
    if len(slides)>1 and len(slides)<3:
        errors.append("a complete deck must have opening, meaningful content, and closing")
    markers={}
    for i,slide in enumerate(slides,1):
        # The authoring scaffold is intentionally not deliverable until the
        # agent replaces its placeholders with genuine researched content.
        for key in ('title','subtitle','notes'):
            if 'TODO:' in slide.get(key,''):
                errors.append(f"slide {i}: unresolved TODO placeholder in {key}")
        layout=slide.get('type')
        needed={
          'cards':'cards','summary':'cards','timeline':'events','split':'bullets',
          'diagram':'items','comparison':'left','quote':'quote'
        }
        if layout in needed and not slide.get(needed[layout]):
            errors.append(f"slide {i}: {layout} missing {needed[layout]}")
        for field in ('title','subtitle'):
            text=slide.get(field,'')
            if len(text)>145:
                errors.append(f"slide {i}: {field} too long ({len(text)} chars), rewrite")
        if len(slide.get('notes',''))<15:
            errors.append(f"slide {i}: speaker notes are too thin")
        for field in ('title','subtitle','caption'):
            text=slide.get(field,'').lower()
            if any(bad in text for bad in BAD_CAPTIONS):
                errors.append(f"slide {i}: unnecessary defensive caption/wording in {field}")
        for setname in ('cards','events','bullets'):
            for j,item in enumerate(slide.get(setname,[]),1):
                if len(item.get('text',''))>230:
                    errors.append(f"slide {i} {setname}[{j}]: text too long; split the idea")
                if item.get('morph_id') and item.get('reveal') != 'static':
                    errors.append(f"slide {i} {setname}[{j}]: morph image and parent card must be static")
        if slide.get('image_mode')=='cover' and not slide.get('decorative'):
            errors.append(f"slide {i}: subject-cropping cover mode requires decorative=true")
        for asset,morph in assets_from_slide(slide):
            if asset not in available:
                errors.append(f"slide {i}: asset '{asset}' absent from sources.json")
            if morph:
                if not re.fullmatch(r'[a-z][a-z0-9_]{2,39}',morph):
                    errors.append(f"slide {i}: malformed morph_id '{morph}'")
                if morph in markers.setdefault(i,{}):
                    errors.append(f"slide {i}: duplicate morph_id '{morph}'")
                markers[i][morph]=asset
        for field in ('left','right'):
            item=slide.get(field,{})
            if item and len(item.get('text',''))>440:
                errors.append(f"slide {i}: comparison {field} too verbose")
        if layout=='diagram' and not slide.get('root'):
            errors.append(f"slide {i}: diagram root missing")
        if layout=='cover' and slide.get('image_mode')=='cover' and not slide.get('decorative'):
            errors.append(f"slide {i}: cover image cover-crop must declare decorative=true")
    morph_slides=data.get('morph_to_slides',[])
    if len(morph_slides)>max(1,int((len(slides)-1)*0.30)):
        errors.append("too many Morph transitions (use semantic Fade unless needed)")
    for n in morph_slides:
        if n<=1 or n>len(slides):
            errors.append(f"invalid Morph destination slide {n}")
            continue
        src=markers.get(n-1,{})
        dest=markers.get(n,{})
        links=[key for key in src if key in dest and src[key]==dest[key]]
        if not links:
            errors.append(f"slide {n}: Morph needs same image asset + morph_id on adjacent slides")
    if errors:
        raise ValueError("Deck specification QA failed:\n- " + "\n- ".join(errors))
    summary={"slides":len(slides),"requested_slide_count":requested,
             "asset_count":len(sources),"morphs":morph_slides,"id":data['id']}
    print('SPEC PASS',json.dumps(summary,ensure_ascii=False))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('deck_json',type=Path)
    a=p.parse_args()
    try: validate(a.deck_json)
    except Exception as ex:
        print(str(ex),file=sys.stderr)
        sys.exit(1)
