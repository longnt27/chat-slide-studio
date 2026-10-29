#!/usr/bin/env python3
"""Add grouped auto-Fade / On-Click steps and optional selective native Morph.

Shape naming convention (PptxGenJS `objectName`):
  AUTO_G0_panel/photo/text    = one simultaneous auto-Fade group
  CLICK_G1_panel/photo/text  = one complete on-click group
  CLICK_G2_panel/photo/text  = the next click group
  !!same_subject             = semantically matched object across Morph slides

Do not treat OOXML validation as real Microsoft PowerPoint playback verification.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys
from zipfile import ZipFile,ZIP_DEFLATED

from lxml import etree

P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
P14 = 'http://schemas.microsoft.com/office/powerpoint/2010/main'
P159 = 'http://schemas.microsoft.com/office/powerpoint/2015/09/main'
MC = 'http://schemas.openxmlformats.org/markup-compatibility/2006'

def tag(key): return '{'+P+'}'+key

def el(key,**attrs):return etree.Element(tag(key),**attrs)

def make_timing(automatic,clicks,duration=470):
    # Main sequence: first group automatically enters; each subsequent group
    # requires a separate PowerPoint next-event. No unrelated decoration is animated.
    timing=el('timing')
    lst=etree.SubElement(timing,tag('tnLst'))
    top=etree.SubElement(lst,tag('par'))
    root=etree.SubElement(top,tag('cTn'),id='1',dur='indefinite',restart='never',nodeType='tmRoot')
    children=etree.SubElement(root,tag('childTnLst'))
    sequence=etree.SubElement(children,tag('seq'),concurrent='1',nextAc='seek')
    main=etree.SubElement(sequence,tag('cTn'),id='2',dur='indefinite',nodeType='mainSeq')
    mainchild=etree.SubElement(main,tag('childTnLst'))
    groups=[automatic]+[clicks[i] for i in sorted(clicks)]
    next_id=3
    for idx,group in enumerate(groups):
        step=etree.SubElement(mainchild,tag('par'))
        step_tn=etree.SubElement(step,tag('cTn'),id=str(next_id),fill='hold')
        next_id+=1
        start=etree.SubElement(step_tn,tag('stCondLst'))
        etree.SubElement(start,tag('cond'),delay='indefinite')
        if idx==0:
            cond=etree.SubElement(start,tag('cond'),evt='onBegin',delay='0')
            etree.SubElement(cond,tag('tn'),val='2')
        contents=etree.SubElement(step_tn,tag('childTnLst'))
        for sid in sorted(group):
            sibling=etree.SubElement(contents,tag('par'))
            with_eff=etree.SubElement(sibling,tag('cTn'),id=str(next_id),dur=str(duration),fill='hold',
                nodeType='withEffect',grpId=str(next_id),presetID='9',presetClass='entr',presetSubtype='0')
            next_id+=1
            st=etree.SubElement(with_eff,tag('stCondLst'))
            etree.SubElement(st,tag('cond'),delay='0')
            cl=etree.SubElement(with_eff,tag('childTnLst'))
            setter=etree.SubElement(cl,tag('set'))
            beh=etree.SubElement(setter,tag('cBhvr'))
            single=etree.SubElement(beh,tag('cTn'),id=str(next_id),dur='1',fill='hold')
            next_id+=1
            inner=etree.SubElement(single,tag('stCondLst'))
            etree.SubElement(inner,tag('cond'),delay='0')
            target=etree.SubElement(beh,tag('tgtEl'))
            etree.SubElement(target,tag('spTgt'),spid=str(sid))
            names=etree.SubElement(beh,tag('attrNameLst'))
            etree.SubElement(names,tag('attrName')).text='style.visibility'
            value=etree.SubElement(setter,tag('to'))
            etree.SubElement(value,tag('strVal'),val='visible')
            effect=etree.SubElement(cl,tag('animEffect'),transition='in',filter='fade')
            cb=etree.SubElement(effect,tag('cBhvr'))
            etree.SubElement(cb,tag('cTn'),id=str(next_id),dur=str(duration))
            next_id+=1
            target=etree.SubElement(cb,tag('tgtEl'))
            etree.SubElement(target,tag('spTgt'),spid=str(sid))
    for typ in ('prev','next'):
        cl=etree.SubElement(sequence,tag(typ+'CondLst'))
        condition=etree.SubElement(cl,tag('cond'),evt=('onPrev' if typ=='prev' else 'onNext'),delay='0')
        target=etree.SubElement(condition,tag('tgtEl'))
        etree.SubElement(target,tag('sldTgt'))
    return timing


def effect_transition(slide_id,morph_slides,has_matched_subject):
    if slide_id in morph_slides:
        if not has_matched_subject:
            raise ValueError(f'Morph destination slide {slide_id} does not have an identical !!subject on previous slide')
        content=etree.Element('{'+MC+'}AlternateContent',nsmap={'mc':MC})
        choice=etree.SubElement(content,'{'+MC+'}Choice',nsmap={'p159':P159})
        choice.set('Requires','p159')
        transition=etree.SubElement(choice,tag('transition'),spd='slow',advClick='1')
        transition.set('{'+P14+'}dur','1800')
        etree.SubElement(transition,'{'+P159+'}morph',option='byObject')
        fallback=etree.SubElement(content,'{'+MC+'}Fallback')
        transition=etree.SubElement(fallback,tag('transition'),spd='med',advClick='1')
        etree.SubElement(transition,tag('fade'))
        return content
    transition=el('transition',spd='med',advClick='1')
    transition.set('{'+P14+'}dur','650')
    etree.SubElement(transition,tag('fade'))
    return transition


def parse_names(root):
    names={}
    for shape in root.xpath('.//p:sp | .//p:pic',namespaces={'p':P}):
        props=shape.find('.//'+tag('cNvPr'))
        if props is not None and props.get('id'):
            names[int(props.get('id'))]=props.get('name','')
    return names


def patch(src,dst,morph_slides=set(),replace_existing=False):
    src,dst=Path(src),Path(dst)
    if src.resolve()==dst.resolve():raise ValueError('Input and output files must be different')
    docs={}
    with ZipFile(src) as source:
        for name in source.namelist():
            if re.fullmatch(r'ppt/slides/slide\d+\.xml',name):
                docs[int(re.search(r'slide(\d+)',name).group(1))]=etree.fromstring(source.read(name))
        shapes_by_slide={n:parse_names(xml) for n,xml in docs.items()}
        if any(n not in docs or n-1 not in docs for n in morph_slides):
            raise ValueError('Morph transition requires a valid destination slide n>=2')
        morph_match={n:({v for v in shapes_by_slide[n].values() if v.startswith('!!')} &
                         {v for v in shapes_by_slide[n-1].values() if v.startswith('!!')})
                     for n in morph_slides}
        if any(not pair for pair in morph_match.values()):
            raise ValueError('Morph subject mismatch: '+repr(morph_match))
        max_morph=max(1,int((len(docs)-1)*.3))
        if len(morph_slides)>max_morph:
            raise ValueError(f'Morph on {len(morph_slides)} transitions is excessive for {len(docs)} slides')
        for number,root in docs.items():
            names=shapes_by_slide[number]
            automatic={sid for sid,name in names.items() if name.startswith('AUTO_G0_')}
            groups=defaultdict(set)
            for sid,name in names.items():
                match=re.match(r'CLICK_G(\d+)_',name)
                if match:groups[int(match.group(1))].add(sid)
            existing=root.find(tag('timing'))
            if existing is not None:
                if not replace_existing:
                    raise ValueError(f'Slide {number} already has animation: pass --replace-existing to regenerate it')
                root.remove(existing)
            if automatic or groups:
                root.append(make_timing(automatic,groups))
            original=root.find(tag('transition'))
            if original is not None:
                root.remove(original)
            orig_alternate=root.find('{'+MC+'}AlternateContent')
            if orig_alternate is not None and orig_alternate.xpath('.//p:transition',namespaces={'p':P}):
                root.remove(orig_alternate)
            transition=effect_transition(number,morph_slides,bool(morph_match.get(number)))
            timing=root.find(tag('timing'))
            if timing is not None:
                root.insert(list(root).index(timing),transition)
            else:
                root.append(transition)
            print('slide',number,'auto',len(automatic),'click steps',len(groups),
                  'morph' if number in morph_slides else 'fade')
        dst.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(dst,'w',compression=ZIP_DEFLATED) as out:
            for member in source.infolist():
                match=re.fullmatch(r'ppt/slides/slide(\d+)\.xml',member.filename)
                if match:
                    root=docs[int(match.group(1))]
                    data=etree.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
                else:data=source.read(member.filename)
                out.writestr(member,data)
    print('WROTE',dst)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input')
    ap.add_argument('output')
    ap.add_argument('--morph',default='',help='comma-separated destination slide indices (e.g. 3,8)')
    ap.add_argument('--replace-existing',action='store_true')
    a=ap.parse_args()
    morph_slides={int(s.strip()) for s in a.morph.split(',') if s.strip()}
    try:patch(a.input,a.output,morph_slides,a.replace_existing)
    except Exception as exc:
        print('ANIMATION PATCH FAILED:',exc,file=sys.stderr)
        sys.exit(1)
