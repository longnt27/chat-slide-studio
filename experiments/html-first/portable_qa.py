#!/usr/bin/env python3
"""Portable PPTX structural and render QA.

Goal: slides open as editable PowerPoint shapes/text in Keynote and Google
Slides rather than chart images. We cannot run Keynote or authenticated Google
Slides in GitHub CI, so this is an import-risk regression gate, NOT a claim that
those applications were tested.

Verify no charts/pictures/SVGs, correct visible bar values and labels, 4
nondegenerate native rectangle bars, in-bounds geometry, and an actual render.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageChops, ImageStat
from pptx import Presentation

LABELS = ["Discover", "Explore", "Design", "Deliver"]
VALUES = [24, 42, 58, 68]
EXPECTED_HEIGHTS_PX = [113, 193, 265, 303]


def run(pptx: Path, preview: Path, reference: Path, report_path: Path):
    prs=Presentation(pptx)
    issues=[]
    if len(prs.slides)!=5:
        issues.append(f"Wrong slide count: {len(prs.slides)}")
    if abs(float(prs.slide_width)/prs.slide_height-16/9) > .005:
        issues.append("Presentation is not 16:9")

    # Export contains no images at all. An Excel chart, SVG or picture can be
    # imported as a blurry bitmap or go missing in different slide programs.
    with ZipFile(pptx) as archive:
        all_names=archive.namelist()
        unsupported=[name for name in all_names if (
            name.startswith("ppt/charts/") or name.startswith("ppt/embeddings/")
            or name.startswith("ppt/media/")
        ) and not name.endswith("/")]
        if unsupported:
            issues.append(f"Portable PPTX has raster/vector media or chart parts: {unsupported}")

    for number,slide in enumerate(prs.slides,1):
        charts=[shape for shape in slide.shapes if shape.has_chart]
        images=[shape for shape in slide.shapes if shape.shape_type==13]
        if charts or images:
            issues.append(f"Slide {number} has {len(charts)} chart objects and {len(images)} pictures")
        for shape in slide.shapes:
            # Shape bounds are in EMU and checked against the nominal slide.
            if shape.left < -20000 or shape.top < -20000 or shape.left + shape.width > prs.slide_width + 20000 or shape.top + shape.height > prs.slide_height + 20000:
                issues.append(f"Slide {number} has off-canvas shape: {shape.name}")
        if not slide.has_notes_slide or not slide.notes_slide.notes_text_frame.text.strip():
            issues.append(f"Slide {number} lost speaker notes")

    if len(prs.slides)>3:
        slide=prs.slides[3]
        shapes={shape.name:shape for shape in slide.shapes}
        text=" ".join(shape.text_frame.text for shape in slide.shapes if shape.has_text_frame)
        for i,(label,value,height) in enumerate(zip(LABELS,VALUES,EXPECTED_HEIGHTS_PX)):
            bar=shapes.get(f"STATIC_s4_bar_{i}")
            val=shapes.get(f"STATIC_s4_value_{i}")
            category=shapes.get(f"STATIC_s4_label_{i}")
            if not bar or not val or not category:
                issues.append(f"Bar {i+1}: missing native bar, value or category objects")
                continue
            if bar.has_chart or bar.shape_type==13:
                issues.append(f"Bar {i+1} is not a native vector shape")
            actual_h=bar.height/914400*96
            if abs(actual_h-height)>2:
                issues.append(f"Bar {i+1}: wrong height {actual_h:.1f}px; expected {height}px")
            if val.text_frame.text.strip()!=str(value) or category.text_frame.text.strip()!=label:
                issues.append(f"Bar {i+1}: wrong value/category text")
            if not bar.fill:
                issues.append(f"Bar {i+1}: fill missing")
            if str(value) not in text or label not in text:
                issues.append(f"Bar {i+1}: visible data missing")

    with Image.open(preview) as img, Image.open(reference) as ref:
        result=img.convert("RGB")
        before=ref.convert("RGB")
        if result.size != before.size:
            result=result.resize(before.size)
        difference=ImageChops.difference(before,result)
        mae=sum(ImageStat.Stat(difference).mean)/3/255
        # Test an actual rasterized result: a different bar color from the background.
        sx=result.width/1280
        sy=result.height/720
        for i,(height,value) in enumerate(zip(EXPECTED_HEIGHTS_PX,VALUES)):
            cx=int((111+i*239+78)*sx)
            cy=int((520-height/2)*sy)
            r,g,b=result.getpixel((cx,cy))
            # Teal chart columns should have markedly higher blue/green than red.
            if not (g > r+20 and b > r+20):
                issues.append(f"Portable bar {i+1} not visible in rendered PPTX at {(cx,cy)}: {(r,g,b)}")

    report={
        "status":"PASS" if not issues else "FAIL",
        "issues":issues,
        "target":"Portable Keynote/Google Slides import-risk reduction",
        "slide_count":len(prs.slides),
        "slide_4_native_bar_objects":4,
        "slide_4_values":VALUES,
        "slide_4_labels":LABELS,
        "no_chart_or_media_parts":not unsupported,
        "normalized_visual_MAE_against_HTML":round(mae,5),
        "third_party_Keynote_tested":False,
        "third_party_Google_Slides_tested":False,
        "native_Excel_chart_data_editability":False,
        "bar_shape_and_text_editability":True,
        "PowerPoint_animations_playback_tested":False
    }
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if issues:
        raise ValueError("Portable slide QA failed: "+"; ".join(issues))


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pptx",type=Path,required=True)
    ap.add_argument("--slide4-preview",type=Path,required=True)
    ap.add_argument("--slide4-html",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    run(a.pptx,a.slide4_preview,a.slide4_html,a.report)
