#!/usr/bin/env python3
"""PowerPoint-authored OOXML-style entrance Fade, semantic On Click, and Morph.

Important regression: a previous implementation used presetID=9 and every effect
as nodeType=withEffect. The package was parseable but did not reproduce native
PowerPoint's click animation structure. The current tree follows the known-good
PowerPoint 16.0 Fade oracle (presetID=10, clickEffect, bldP for text).

AUTO_G0_<uid>_<part>         first unit fades on slide entry without a click
CLICK_G1_<uid>_<part>       first presenter click, complete semantic group
CLICK_G2_<uid>_<part>       second click, etc.
!!<subject>                Morph match across *adjacent* slides
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import math
from pathlib import Path
import re
import sys
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
P14='http://schemas.microsoft.com/office/powerpoint/2010/main'
P159='http://schemas.microsoft.com/office/powerpoint/2015/09/main'
MC='http://schemas.openxmlformats.org/markup-compatibility/2006'
EMU=914400

def tag(s):return '{'+P+'}'+s

def el(s,**attrs):return etree.Element(tag(s),**attrs)

def node(parent,key,**attrs):return etree.SubElement(parent,tag(key),**attrs)


def condition(time_node, delay):
    start=node(time_node,'stCondLst')
    node(start,'cond',delay=delay)


def entrance_effect(parent,sid,tn_id,kind,duration):
    # Same structure as a real PowerPoint 16.0 Fade entrance effect.
    effect_par=node(parent,'par')
    effect=node(effect_par,'cTn',id=str(tn_id),presetID='10',presetClass='entr',
        presetSubtype='0',fill='hold',grpId='0',nodeType=kind)
    tn_id+=1
    condition(effect,'0')
    content=node(effect,'childTnLst')
    setter=node(content,'set')
    behavior=node(setter,'cBhvr')
    one=node(behavior,'cTn',id=str(tn_id),dur='1',fill='hold')
    tn_id+=1
    condition(one,'0')
    node(node(behavior,'tgtEl'),'spTgt',spid=str(sid))
    node(node(behavior,'attrNameLst'),'attrName').text='style.visibility'
    node(node(setter,'to'),'strVal',val='visible')
    fade=node(content,'animEffect',transition='in',filter='fade')
    fb=node(fade,'cBhvr')
    node(fb,'cTn',id=str(tn_id),dur=str(duration))
    tn_id+=1
    node(node(fb,'tgtEl'),'spTgt',spid=str(sid))
    return tn_id


def make_timing(automatic,clicks,text_shapes,duration=480):
    timing=el('timing');top=node(timing,'tnLst')
    par=node(top,'par')
    tm=node(par,'cTn',id='1',dur='indefinite',restart='never',nodeType='tmRoot')
    seq=node(node(tm,'childTnLst'),'seq',concurrent='1',nextAc='seek')
    main=node(seq,'cTn',id='2',dur='indefinite',nodeType='mainSeq')
    content=node(main,'childTnLst')
    steps=([('auto',automatic)] if automatic else [])+[(f'click-{n}',clicks[n]) for n in sorted(clicks)]
    idnum=3
    for mode,group in steps:
        # PowerPoint-generated step has two nested par/cTn levels; the first
        # is delay=indefinite for an On Click step, and delay=0 for automatic.
        outer=node(content,'par')
        ctn=node(outer,'cTn',id=str(idnum),fill='hold')
        idnum+=1
        condition(ctn,'0' if mode=='auto' else 'indefinite')
        inner=node(node(ctn,'childTnLst'),'par')
        inner_ctn=node(inner,'cTn',id=str(idnum),fill='hold')
        idnum+=1
        condition(inner_ctn,'0')
        siblings=node(inner_ctn,'childTnLst')
        for i,sid in enumerate(sorted(group)):
            # One clickEffect starts the group; its peers use With Previous.
            kind='clickEffect' if mode!='auto' and i==0 else ('afterEffect' if mode=='auto' and i==0 else 'withEffect')
            idnum=entrance_effect(siblings,sid,idnum,kind,duration)
    # PowerPoint-authored main sequence prev/next slide conditions.
    for direction,event in [('prev','onPrev'),('next','onNext')]:
        cl=node(seq,direction+'CondLst')
        cond=node(cl,'cond',evt=event,delay='0')
        node(node(cond,'tgtEl'),'sldTgt')
    # PowerPoint-authored Fade notes: bldP is appropriate for text-bearing
    # p:sp, NOT pictures or grouped shape frames.
    text_targets=text_shapes & (set(automatic) | set().union(*clicks.values()) if clicks else set(automatic))
    if text_targets:
        builds=node(timing,'bldLst')
        for sid in sorted(text_targets):node(builds,'bldP',spid=str(sid),grpId='0')
    return timing


def effect_transition(number,morph_slides):
    if number in morph_slides:
        alt=etree.Element('{'+MC+'}AlternateContent',nsmap={'mc':MC})
        choice=etree.SubElement(alt,'{'+MC+'}Choice',nsmap={'p159':P159});choice.set('Requires','p159')
        # PowerPoint-authored Morph places xmlns:p14 on p:transition and
        # uses p14:dur (not a serializer-generated ns1:dur alias).
        # Preserve inline namespace placement for Office compatibility.
        transition=etree.SubElement(choice,tag('transition'),
            nsmap={'p14':P14},spd='slow',advClick='1')
        transition.set('{'+P14+'}dur','1450')
        etree.SubElement(transition,'{'+P159+'}morph',option='byObject')
        fallback=etree.SubElement(alt,'{'+MC+'}Fallback')
        fade=node(fallback,'transition',spd='med',advClick='1');node(fade,'fade')
        return alt
    transition=el('transition',spd='med',advClick='1')
    transition.set('{'+P14+'}dur','650')
    node(transition,'fade')
    return transition


def shapes(root):
    names={};text_ids=set();geometry={};kind={}
    for shape in root.xpath('.//p:sp | .//p:pic',namespaces={'p':P}):
        nv=shape.find('.//'+tag('cNvPr'))
        if nv is None or not nv.get('id'):continue
        sid=int(nv.get('id'))
        names[sid]=nv.get('name','')
        kind[sid]='picture' if shape.tag==tag('pic') else 'shape'
        if shape.tag==tag('sp') and shape.find(tag('txBody')) is not None:
            text_ids.add(sid)
        transform=shape.find('.//{'+A+'}xfrm')
        if transform is not None:
            off=transform.find('{'+A+'}off');ext=transform.find('{'+A+'}ext')
            if off is not None and ext is not None:
                geometry[sid]=(int(off.get('x'))/EMU,int(off.get('y'))/EMU,
                               int(ext.get('cx'))/EMU,int(ext.get('cy'))/EMU)
    return names,text_ids,geometry,kind


def morph_checks(number,pair_names,details):
    previous=details[number-1];current=details[number]
    for name in pair_names:
        pids=[sid for sid,n in previous[0].items() if n==name]
        cids=[sid for sid,n in current[0].items() if n==name]
        if len(pids)!=1 or len(cids)!=1:
            raise ValueError(f'Morph needs a unique 1:1 pair for {name} (slides {number-1}->{number})')
        old=previous[2].get(pids[0]);new=current[2].get(cids[0])
        if old is None or new is None:raise ValueError('Morph requires positioned image geometry')
        dx=(old[0]+old[2]/2)-(new[0]+new[2]/2)
        dy=(old[1]+old[3]/2)-(new[1]+new[3]/2)
        travel=math.hypot(dx,dy)
        scale=max(old[2]/new[2],new[2]/old[2],old[3]/new[3],new[3]/old[3])
        if travel < .18 and scale < 1.18:
            raise ValueError(f'Morph {name} changes neither framing nor focus (slides {number-1}->{number})')
        if travel>8.0:raise ValueError(f'Morph {name} flies too far across screen: {travel:.1f}in')
        if scale>4.0:raise ValueError(f'Morph {name} scales excessively ({scale:.2f}x)')
        if previous[3][pids[0]] != current[3][cids[0]]:
            raise ValueError('Morph subject object type differs across slides')


def patch(src,dst,morph_slides=None,replace_existing=False):
    morph_slides=set(morph_slides or [])
    src,dst=Path(src),Path(dst)
    if src.resolve()==dst.resolve():raise ValueError('Input and output must differ')
    with ZipFile(src) as source:
        docs={int(re.search(r'slide(\d+)',name).group(1)):etree.fromstring(source.read(name))
              for name in source.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',name)}
        details={n:shapes(root) for n,root in docs.items()}
        if any(n not in docs or n-1 not in docs for n in morph_slides):
            raise ValueError('Morph requires a valid destination slide n>=2')
        if len(morph_slides)>max(1,int((len(docs)-1)*.3)):
            raise ValueError('Excessive Morph transitions')
        for n in morph_slides:
            before={v for v in details[n-1][0].values() if v.startswith('!!')}
            after={v for v in details[n][0].values() if v.startswith('!!')}
            matches=before&after
            if not matches:raise ValueError(f'Morph slide {n} has no adjacent subject match')
            morph_checks(n,matches,details)
        for n,root in docs.items():
            names,text_ids,*_=details[n]
            automatic={sid for sid,name in names.items() if name.startswith('AUTO_G0_')}
            clicks=defaultdict(set)
            for sid,name in names.items():
                match=re.match(r'CLICK_G(\d+)_',name)
                if match:clicks[int(match.group(1))].add(sid)
            if clicks and sorted(clicks)!=list(range(1,max(clicks)+1)):
                raise ValueError(f'Slide {n} has non-contiguous click groups: {sorted(clicks)}')
            old=root.find(tag('timing'))
            if old is not None:
                if not replace_existing:raise ValueError(f'Slide {n} already has timing')
                root.remove(old)
            if automatic or clicks:
                root.append(make_timing(automatic,clicks,text_ids))
            old=root.find(tag('transition'))
            if old is not None:root.remove(old)
            for alt in root.findall('{'+MC+'}AlternateContent'):
                if alt.find('.//'+tag('transition')) is not None:root.remove(alt)
            tr=effect_transition(n,morph_slides)
            timing=root.find(tag('timing'))
            root.insert(list(root).index(timing) if timing is not None else len(root),tr)
            print(f'SLIDE {n:02d} | auto {len(automatic)} | click groups {len(clicks)} | '+
                  ('Morph' if n in morph_slides else 'Fade'))
        dst.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(dst,'w',compression=ZIP_DEFLATED) as out:
            for f in source.infolist():
                match=re.fullmatch(r'ppt/slides/slide(\d+)\.xml',f.filename)
                if match:
                    data=etree.tostring(docs[int(match.group(1))],encoding='UTF-8',xml_declaration=True,standalone=True)
                else:data=source.read(f.filename)
                out.writestr(f,data)
    print('ANIMATION PATCH WROTE',dst)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input');ap.add_argument('output')
    ap.add_argument('--morph',default='')
    ap.add_argument('--replace-existing',action='store_true')
    a=ap.parse_args()
    try:patch(a.input,a.output,{int(s.strip()) for s in a.morph.split(',') if s.strip()},a.replace_existing)
    except Exception as e:
        print('ANIMATION PATCH FAILED:',e,file=sys.stderr);sys.exit(1)
