#!/usr/bin/env python3
"""Compare HTML browser screenshots against a generated editable PowerPoint.

A visual difference score is descriptive, NOT proof of pixel-perfect fidelity.
Native effect XML is not evidence of actual desktop slideshow playback.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageChops, ImageStat
from pptx import Presentation

def evaluate(pptx_file: Path, html_dir: Path, pptx_dir: Path, out: Path):
    prs = Presentation(pptx_file)
    out.mkdir(parents=True, exist_ok=True)
    results=[]
    if len(prs.slides) != 5:
        raise ValueError(f"Expected 5 slides, got {len(prs.slides)}")

    for i,slide in enumerate(prs.slides,1):
        text_shapes = [shape for shape in slide.shapes
                       if shape.has_text_frame and shape.text_frame.text.strip()]
        chart_shapes = [shape for shape in slide.shapes if shape.has_chart]
        pictures = [shape for shape in slide.shapes if shape.shape_type == 13]
        left_file = html_dir / f"slide-{i:02d}.png"
        right_file = pptx_dir / f"slide-{i:02d}.png"
        with Image.open(left_file) as source, Image.open(right_file) as rendered:
            a=source.convert("RGB")
            b=rendered.convert("RGB").resize(a.size)
            diff=ImageChops.difference(a,b)
            mae=sum(ImageStat.Stat(diff).mean)/3/255
            pair=Image.new("RGB",(a.width*2+20,a.height),"#dfe3eb")
            pair.paste(a,(0,0)); pair.paste(b,(a.width+20,0))
            pair.save(out/f"slide-{i:02d}-html-vs-pptx.png")
        results.append({
            "slide":i,
            "editable_text_shapes":len(text_shapes),
            "native_chart_shapes":len(chart_shapes),
            "picture_shapes":len(pictures),
            "all_shapes":len(slide.shapes),
            "image_mean_absolute_error_0_to_1":round(mae,4),
            "visual_review_required":True
        })
    with ZipFile(pptx_file) as archive:
        slide_xml=[archive.read(f"ppt/slides/slide{i}.xml") for i in range(1,6)]
    report={
        "status":"PASS" if all(x["editable_text_shapes"]>=2 for x in results) else "FAIL",
        "slides":len(prs.slides),
        "PPTX_is_not_flat_screenshots":all(x["editable_text_shapes"]>=2 for x in results),
        "native_animation_timing_slides":[i for i,blob in enumerate(slide_xml,1) if b"<p:timing" in blob],
        "native_transition_slides":[i for i,blob in enumerate(slide_xml,1) if b"<p:transition" in blob],
        "native_powerpoint_playback_tested":False,
        "chart_data_editability":"NOT_TESTED: HTML bars are native shapes, not PowerPoint chart data",
        "slides_detail":results
    }
    (out/"evaluation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if report["status"]!="PASS":
        raise ValueError("HTML-to-PPTX failed native text editability QA")
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pptx",type=Path,required=True)
    ap.add_argument("--html-previews",type=Path,required=True)
    ap.add_argument("--pptx-previews",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    evaluate(a.pptx,a.html_previews,a.pptx_previews,a.out)
