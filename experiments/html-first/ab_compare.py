#!/usr/bin/env python3
"""Fair A/B evaluation: generic HTML converter vs ChatGPT-authored native PPTX.

A = dom-to-pptx on the fixed 5-slide HTML fixture.
B = ChatGPT-written PptxGenJS with editable charts and explicit timing groups.

Visual differences are reported, not used alone to declare an overall winner.
Static OOXML timing cannot prove actual desktop PowerPoint playback.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageChops, ImageStat
from pptx import Presentation
from lxml import etree
import json
import re
from zipfile import ZipFile

P="http://schemas.openxmlformats.org/presentationml/2006/main"
NS={"p":P}
EXPECTED_ANIMATED_CLICKS={1:0,2:2,3:0,4:0,5:2}
REQUIRED_TEXT={
  1:["Ideas deserve","better slides.","Editable PowerPoint","Exploring a single source"],
  2:["Good presentation design","starts with structure","One message",
     "Visual hierarchy","Real editability","Text and simple shapes"],
  3:["Design once. Deliver twice.","HTML & CSS","DOM → shapes","Native PPTX",
     "The browser is the design surface"],
  4:["Numbers should communicate.","Illustrative values only."],
  5:["From pixels","to precision.","A real proof of concept","Prototype"]
}
EXPECTED_SERIES=[24,42,58,68]
EXPECTED_CATEGORIES=["Discover","Explore","Design","Deliver"]


def slide_shapes(slide):
    return {
        "total":len(slide.shapes),
        "editable_text":sum(1 for x in slide.shapes
                            if x.has_text_frame and x.text_frame.text.strip()),
        "pictures":sum(1 for x in slide.shapes if x.shape_type==13),
        "native_charts":sum(1 for x in slide.shapes if x.has_chart),
    }


def notes_text(slide):
    if not slide.has_notes_slide:
        return ""
    return slide.notes_slide.notes_text_frame.text or ""


def text_check(slide,slide_number):
    raw=" ".join(shape.text_frame.text for shape in slide.shapes
                 if shape.has_text_frame)
    flat=" ".join(raw.casefold().split())
    return [needle for needle in REQUIRED_TEXT[slide_number]
            if " ".join(needle.casefold().split()) not in flat]


def chart_values(slide):
    charts=[shape.chart for shape in slide.shapes if shape.has_chart]
    if not charts:return None
    first=charts[0]
    return [float(x) for x in first.series[0].values]


def chart_categories(slide):
    charts=[shape.chart for shape in slide.shapes if shape.has_chart]
    if not charts:return None
    return [str(cat.label) for cat in charts[0].plots[0].categories]


def timing(pptx_file):
    out=[]
    with ZipFile(pptx_file) as archive:
        for i in range(1,6):
            xml=etree.fromstring(archive.read("ppt/slides/slide"+str(i)+".xml"))
            out.append({
                "slide":i,
                "has_timing":bool(xml.xpath(".//p:timing",namespaces=NS)),
                "click_effects":len(xml.xpath(".//p:cTn[@nodeType='clickEffect']",namespaces=NS)),
                "fade_entrances":len(xml.xpath(".//p:animEffect[@filter='fade']",namespaces=NS)),
                "has_transition":bool(xml.xpath(".//p:transition",namespaces=NS)),
            })
    return out


def screenshot_mae(a_file,b_file,target):
    with Image.open(a_file) as a_img, Image.open(b_file) as b_img:
        a=a_img.convert("RGB")
        b=b_img.convert("RGB").resize(a.size)
        diff=ImageChops.difference(a,b)
        score=sum(ImageStat.Stat(diff).mean)/3/255
        return a,b,round(score,4)


def main(args):
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    decks={
        "converter":Presentation(args.converter),
        "agent_native":Presentation(args.agent),
    }
    issues=[]
    if any(len(prs.slides)!=5 for prs in decks.values()):
        raise ValueError("Both decks must contain exactly five slides")
    scores={key:[] for key in decks}
    notes_count={}
    object_counts={}
    for name,prs in decks.items():
        ratio=float(prs.slide_width)/prs.slide_height
        if abs(ratio-16/9)>0.02:issues.append(name+": incorrect 16:9 aspect ratio")
        notes_count[name]=sum(1 for slide in prs.slides if notes_text(slide).strip())
        object_counts[name]=[slide_shapes(slide) for slide in prs.slides]
        if name=="agent_native":
            for i,slide in enumerate(prs.slides,1):
                missing=text_check(slide,i)
                if missing:issues.append("B slide "+str(i)+" missing content "+repr(missing))
                if not notes_text(slide).strip():
                    issues.append("B slide "+str(i)+" is missing speaker notes")
                if slide_shapes(slide)["editable_text"]<3:
                    issues.append("B slide "+str(i)+" lacks enough editable text")
    values=chart_values(decks["agent_native"].slides[3])
    categories=chart_categories(decks["agent_native"].slides[3])
    if values!=EXPECTED_SERIES:
        issues.append("B chart lost original numerical data: "+repr(values))
    if categories!=EXPECTED_CATEGORIES:
        issues.append("B chart categories are not the HTML labels: "+repr(categories))
    if chart_values(decks["converter"].slides[3]) is not None:
        # This is not an error; A might improve in future versions.
        print("INFO: The converter also produced a native editable chart")

    for i in range(1,6):
        html=Image.open(args.html_previews/("slide-%02d.png"%i)).convert("RGB")
        originals=[html]
        for name,dirpath in (("converter",args.converter_previews),
                             ("agent_native",args.agent_previews)):
            file=dirpath/("slide-%02d.png"%i)
            original,converted,score=screenshot_mae(
                args.html_previews/("slide-%02d.png"%i),file,(out/("slide-%02d.png"%i)))
            scores[name].append(score)
            originals.append(converted)
        width,height=html.size
        margin=14
        preview=Image.new("RGB",(width*3+margin*2,height), "#DCE2EA")
        for k,im in enumerate(originals):
            preview.paste(im,(k*(width+margin),0))
        preview.save(out/("slide-%02d-html-A-converter-B-agent.png"%i))
        html.close()

    timings={name:timing(file) for name,file in (
        ("converter",args.converter),("agent_native",args.agent))}
    for item in timings["agent_native"]:
        number=item["slide"]
        expected=EXPECTED_ANIMATED_CLICKS[number]
        if item["click_effects"]!=expected:
            issues.append("B slide %d expected %d On Click groups, found %d"%
                          (number,expected,item["click_effects"]))
        if number in (1,2,5) and not item["has_timing"]:
            issues.append("B slide %d expected native animation timing"%number)

    report={
        "comparison":"Same original five-slide HTML, two PPTX authoring strategies",
        "A":"dom-to-pptx automatic HTML converter",
        "B":"ChatGPT-authored PptxGenJS source, native chart and OOXML timing",
        "status":"PASS" if not issues else "FAIL",
        "issues":issues,
        "per_slide_normalized_MAE":{
            "converter":scores["converter"],
            "agent_native":scores["agent_native"]
        },
        "mean_normalized_MAE":{
            name:round(sum(values)/len(values),4) for name,values in scores.items()
        },
        "native_editable_chart_values_in_B":values,
        "native_editable_chart_categories_in_B":categories,
        "native_chart_counts":{
            name:sum(s["native_charts"] for s in item) for name,item in object_counts.items()
        },
        "editable_text_shape_counts":{
            name:sum(s["editable_text"] for s in item) for name,item in object_counts.items()
        },
        "speaker_notes_count":notes_count,
        "shapes_per_slide":object_counts,
        "animation_timing":timings,
        "true_native_animation_playback":"NOT_TESTED",
        "morph":"NOT_TESTED: no adjacent shared subject in HTML fixture",
        "visual_human_review":"REQUIRED",
        "disclaimer":"Illustrative numerical data, not real-world claims"
    }
    (out/"ab-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if issues:
        raise ValueError("Native authoring QA failed: "+"; ".join(issues))


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--converter",type=Path,required=True)
    ap.add_argument("--agent",type=Path,required=True)
    ap.add_argument("--html-previews",type=Path,required=True)
    ap.add_argument("--converter-previews",type=Path,required=True)
    ap.add_argument("--agent-previews",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    main(ap.parse_args())
