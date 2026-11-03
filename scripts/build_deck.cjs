#!/usr/bin/env node
/**
 * Data-driven PowerPoint renderer. The GitHub-connected ChatGPT edits deck.json,
 * not this engine, for ordinary presentation requests.
 *
 * Shape names are a contract with patch_animations.py and qa_pptx.py:
 *   STATIC_* (visible on slide entry), AUTO_G0_* (whole group Fade on entry),
 *   CLICK_GN_* (whole group enters on the N-th click), !!subject (Morph image).
 */
'use strict';
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pptxgen = require('pptxgenjs');
const {planDiagram} = require('./diagram_geometry.cjs');

const deckDir = path.resolve(process.argv[2] || 'decks/demo');
const deckFile = path.join(deckDir, 'deck.json');
const data = JSON.parse(fs.readFileSync(deckFile, 'utf8'));
const tier=data.tier||'presenter'; // legacy default
const animationMode=data.animation_mode||(tier==='content'?'none':'presenter');
const routePath=path.join(deckDir,'dist','slide-route.json');
if(data.navigation && !fs.existsSync(routePath))
  throw Error('Navigation requires compiled dist/slide-route.json from presentation_profile.py');
const route=fs.existsSync(routePath)?
  JSON.parse(fs.readFileSync(routePath,'utf8')):{
    logical_count:data.slides.length,physical_count:data.slides.length,revisit_count:0,
    physical_slides:data.slides.map((_,i)=>({logical:i+1,physical:i+1,role:'primary'})),
    morph_physical_destinations:data.morph_to_slides||[],
    animation_mode:animationMode
  };
if(route.logical_count!==data.slides.length || route.animation_mode!==animationMode)
  throw Error('Compiled route does not match deck logical count or animation tier');
const animated=animationMode!=='none';
const assetManifest = path.join(deckDir, 'verified-assets', 'assets.json');
const verified = fs.existsSync(assetManifest) ?
  JSON.parse(fs.readFileSync(assetManifest,'utf8')).assets : [];
const assets = Object.fromEntries(verified.map(a=>[a.id,a]));
const outDir=path.join(deckDir,'dist');
const cacheDir=path.join(outDir,'image-cache');
fs.mkdirSync(cacheDir,{recursive:true});

const pptx = new pptxgen();
pptx.layout='LAYOUT_WIDE';
pptx.author='Chat Slide Studio';
pptx.subject=data.title;
pptx.title=data.title;
pptx.lang=data.language||'vi-VN';
const PRESETS={
  heritage:{background:'0A202B',panel:'173640',primary:'F2E8D2',secondary:'D3B274',accent:'76B2AE',text:'E9E2D1',muted:'ADBBC0',heading_font:'Noto Serif',body_font:'Noto Sans'},
  modern:{background:'101A2C',panel:'1C2E43',primary:'FFFFFF',secondary:'7DC9E4',accent:'89D7AA',text:'E5EEF5',muted:'A5B4C7',heading_font:'Noto Sans',body_font:'Noto Sans'},
  science:{background:'10232D',panel:'183842',primary:'F5F6F8',secondary:'88DBCE',accent:'F9BC77',text:'E0E9EC',muted:'A0BCC0',heading_font:'Noto Sans',body_font:'Noto Sans'}
};
const themeSpec=data.theme||{};
const T={...PRESETS[themeSpec.preset||'heritage'],...themeSpec};
for (const colorKey of ['background','panel','primary','secondary','accent','text','muted'])
  T[colorKey]=(T[colorKey]||'FFFFFF').replace(/^#/,'');
pptx.theme={headFontFace:T.heading_font,bodyFontFace:T.body_font,lang:data.language||'vi-VN'};
const W=40/3,H=7.5,M=0.72,CONTENT_W=W-2*M;
const imageAudit=[];
if (!Number.isInteger(data.requested_slide_count) || data.requested_slide_count !== data.slides.length) {
  throw Error(`Slide count mismatch: requested ${data.requested_slide_count}; authored ${data.slides.length}`);
}
const proposedClickSteps = animated ? data.slides.reduce((sum,slide)=>{
  const group=(arr)=>arr?.reduce((n,x,i)=>n+((x.reveal||((i===0)?'auto':'click'))==='click'?1:0),0)||0;
  if(slide.type==='cards'||slide.type==='summary')return sum+group(slide.cards);
  if(slide.type==='timeline')return sum+group(slide.events);
  if(slide.type==='split'||slide.type==='section')return sum+group(slide.bullets);
  if(slide.type==='comparison')return sum+((slide.left?.reveal==='click')?1:0)+((slide.right?.reveal||'click')==='click'?1:0);
  if(slide.type==='diagram')return sum+1+(slide.bottom?1:0);
  return sum;
},0) : 0;
const qa={expected_slides:route.physical_count,expected_logical_slides:data.requested_slide_count,
  physical_route:route.physical_slides,animation_mode:animationMode,require_speaker_notes:true,require_source_notes:true,
  click_note_matching:true,morph_max_fraction:data.navigation?null:0.3,min_click_groups:proposedClickSteps,
  centered_labels:[],card_rows:[],diagram_relationships:[],
  max_decorative_dividers:0,
  expected_morph_slides:route.morph_physical_destinations,
  image_audit:'image-audit.json',
  max_text_overlap_area_in2:0.025};
const shapeTypes=pptx.ShapeType;
const imageCache=new Map();

function objName(kind,uid,part){
  if(kind==='auto') return `AUTO_G0_${uid}_${part}`;
  if(kind && String(kind).startsWith('click')) return `CLICK_G${String(kind).replace(/^click-/,'')}_${uid}_${part}`;
  return `STATIC_${uid}_${part}`;
}
class Motion{
  constructor(n,enabled=animated){this.n=n;this.click=0;this.cues=[];this.enabled=enabled;}
  pick(value='auto',label='Điểm tiếp theo'){
    if(!this.enabled)return 'static';
    if(value==='static') return 'static';
    if(value==='auto')return 'auto';
    if(value==='click'){
      ++this.click;this.cues.push(`Click ${this.click}: ${label}`);
      return `click-${this.click}`;
    }
    throw Error(`slide ${this.n}: invalid reveal ${value}`);
  }
}
function shape(s,x,y,w,h,opts={}){
  s.addShape(opts.type||shapeTypes.roundRect,{
    x,y,w,h,radius:0.12,
    rectRadius:0.08,
    fill:{color:opts.fill||T.panel,transparency:opts.opacity||0},
    line:opts.line?{color:opts.line,width:opts.lineWidth||0.75,transparency:opts.lineTransparency||0}:
      {color:opts.fill||T.panel,transparency:100},
    objectName:opts.name||'',
  });
}
function text(s,value,x,y,w,h,size=17,color=T.text,opts={}){
  s.addText(String(value||''),{
    x,y,w,h,margin:0,vertAlign:'mid',
    align:opts.align||'left',
    fontFace:opts.serif?T.heading_font:T.body_font,
    fontSize:size,bold:!!opts.bold,color,
    fit:'shrink',breakLine:false,
    lineSpacingMultiple:1.05,
    charSpacing:opts.charSpacing||0,
    objectName:opts.name||''
  });
}
function rule(s,x,y,w,color=T.secondary,alpha=0,name='DECO_rule'){
  s.addShape(shapeTypes.line,{x,y,w,h:0,line:{color,width:1.0,transparency:alpha},objectName:name});
}
function label(s,value,x,y,w,name='',align='left',color=T.secondary){
  text(s,String(value||'').toUpperCase(),x,y,w,0.24,10.2,color,
    {bold:true,charSpacing:1.3,name,align});
}
function header(s,n,info){
  s.background={color:T.background};
  label(s,`${String(n).padStart(2,'0')} / ${info.eyebrow||data.title}`,M,0.35,11.8);
  text(s,info.title,M,0.78,CONTENT_W,0.68,30,T.primary,{serif:true,bold:true});
  if(info.subtitle) text(s,info.subtitle,M,1.51,CONTENT_W,0.42,14,T.muted);
  label(s,data.title.slice(0,55),M,7.12,10.5,'','left',T.muted);
  text(s,String(n).padStart(2,'0'),12.05,7.095,0.55,0.24,10.3,T.secondary,
    {align:'right',bold:true});
}
function sourceNotes(info,used,motion){
  const srcs=[];
  for(const a of new Set(used)){
    const item=assets[a];
    if(!item)throw Error('Missing image asset in CI manifest: '+a);
    srcs.push(`${item.subject||a} | ${item.author} | ${item.license} | ${item.source_page}`);
  }
  for(const u of info.source_urls||[])srcs.push(u);
  if(info.chart_data?.source)srcs.push('Chart dataset | '+info.chart_data.source);
  return `${info.notes||''}\n\n[Presenter cues]\n${motion.cues.join('\n')||'Chuyển slide theo nhịp người thuyết trình.'}\n\n[Sources]\n${srcs.join('\n')||'Nội dung gốc do người dùng cung cấp trong deck.json; chưa có nguồn bên ngoài.'}\n[/Sources]`;
}
async function putImage(s,n,key,x,y,w,h,{mode='preserve',decorative=false,morph_id=null,name='',alt=''}={}){
  const a=assets[key];
  if(!animated)morph_id=null; // Static tier may reuse photo IDs without motion.
  if(!a)throw Error(`slide ${n}: image ${key} not found in verified-assets/assets.json`);
  if(mode==='cover'&&!decorative)throw Error(`slide ${n}: unsafe cover crop for documentary subject ${key}`);
  if(morph_id && mode==='cover')throw Error('Morph subjects must be preserved, not cropped');
  const basename=`${key}-${(a.sha256||'').slice(0,10)}-${Math.round(w*200)}x${Math.round(h*200)}-${mode}-${T.panel}.jpg`;
  const final=path.join(cacheDir,basename),pxw=Math.max(60,Math.round(w*200)),pxh=Math.max(60,Math.round(h*200));
  if(!imageCache.has(basename)){
    if(!fs.existsSync(final)){
      if(mode==='cover'){
        await sharp(a.path).rotate().resize(pxw,pxh,{fit:'cover',position:'centre'}).jpeg({quality:89}).toFile(final);
      } else {
        // Solid, understated matting avoids giant blurred/cropped faces or
        // architectural fragments behind the intact factual subject.
        const dark=await sharp({create:{width:pxw,height:pxh,channels:3,
          background:'#'+T.panel}}).jpeg({quality:89}).toBuffer();
        const foreground=await sharp(a.path).rotate().resize(pxw-20,pxh-20,{fit:'inside'})
          .png().toBuffer();
        const meta=await sharp(foreground).metadata();
        await sharp(dark).composite([{input:foreground,
          left:Math.floor((pxw-meta.width)/2),top:Math.floor((pxh-meta.height)/2)}])
          .jpeg({quality:88}).toFile(final);
      }
    }
    imageCache.set(basename,final);
  }
  const sourceAspect=a.width/a.height,frameAspect=w/h;
  const mismatch=Math.max(sourceAspect/frameAspect,frameAspect/sourceAspect);
  // IMPORTANT: Morph pairs MUST reference identical original picture bytes.
  // Previously each frame used a differently resized/matted JPEG: PowerPoint
  // saw changed image content and awkwardly cross-faded the matte instead of
  // smoothly interpolating the same subject. Use the verified original raster,
  // with letterboxing outside the picture shape (a separate static background).
  let display={x,y,w,h};
  if(morph_id){
    if(frameAspect>sourceAspect){
      display.w=h*sourceAspect;
      display.x=x+(w-display.w)/2;
    }else{
      display.h=w/sourceAspect;
      display.y=y+(h-display.h)/2;
    }
  }
  imageAudit.push({slide:n,key,mode,decorative,source_ratio:sourceAspect,
    frame_ratio:frameAspect,aspect_mismatch:mismatch,source:a.source_page,
    exact_original_used_for_morph:!!morph_id, picture_geometry:display});
  s.addImage({path:morph_id?a.path:final,...display,
    objectName:morph_id?'!!'+morph_id:name,altText:alt||a.subject||key});
  return true;
}
async function cardPanel(s,n,m,uid,entry,x,y,w,h,defaultReveal='click',used,opts={}){
  const reveal=m.pick(entry.reveal||defaultReveal,entry.title||'Ý tiếp theo');
  const nm=(part)=>objName(reveal,uid,part);
  shape(s,x,y,w,h,{fill:T.panel,line:T.muted,lineTransparency:80,name:nm('panel')});
  let bodyTop=y+1.55;
  if(entry.image){
    const imgX=x+0.17,imgY=y+0.17,imgH=1.54;
    const imgW=w-0.34;
    shape(s,imgX,imgY,imgW,imgH,{type:shapeTypes.rect,fill:T.background,name:nm('image_bg')});
    // Morph object participates directly in transition. Never assign a
    // separate entrance to an image that must remain visible across slides.
    await putImage(s,n,entry.image,imgX,imgY,imgW,imgH,{
      morph_id:entry.morph_id||null,name:nm('image'),alt:entry.title
    });
    used.push(entry.image);
    bodyTop=y+1.95;
  } else {
    label(s,entry.badge||String(uid).toUpperCase(),x+0.20,y+0.29,w-0.40,nm('badge'));
    bodyTop=y+0.96;
  }
  if(entry.image && entry.badge)label(s,entry.badge,x+0.20,bodyTop,w-0.40,nm('badge'));
  let ty=entry.image?bodyTop+0.32:bodyTop;
  text(s,entry.title,x+0.20,ty,w-0.40,0.56,17.3,T.primary,{bold:true,name:nm('title')});
  text(s,entry.text,x+0.20,ty+0.67,w-0.4,Math.max(0.52,y+h-(ty+0.87)),
    13,T.muted,{name:nm('body')});
  return nm('panel');
}
async function renderSlide(info,n,logical=n,role='primary'){
  const s=pptx.addSlide(),m=new Motion(n),used=[];
  const ty=info.type;
  if(ty==='cover'){
    s.background={color:T.background};
    shape(s,M,1.13,0.10,4.72,{type:shapeTypes.rect,fill:T.secondary});
    label(s,info.eyebrow||data.title,1.10,1.27,5.3);
    text(s,info.title,1.09,2.11,5.72,2.03,40,T.primary,{serif:true,bold:true});
    text(s,info.subtitle||'',1.11,4.81,5.43,1.14,18,T.muted);
    if(info.image){
      shape(s,7.04,1.10,5.43,5.48,{fill:T.panel});
      await putImage(s,n,info.image,7.19,1.24,5.12,5.16,{
        mode:info.image_mode||'preserve',decorative:!!info.decorative,
        alt:'Ảnh mở đầu '+info.title});used.push(info.image);
    } else {
      shape(s,7.12,1.20,5.31,5.28,{fill:T.panel});
      shape(s,8.02,2.02,3.50,3.50,{fill:T.secondary,opacity:75});
    }
    label(s,`${data.slides.length} SLIDES / ${data.duration_minutes||'—'} PHÚT`,1.11,6.81,7.2);
  }else if(ty==='thanks'){
    s.background={color:T.background};
    label(s,info.eyebrow||'KẾT THÚC',M,1.18,7.0);
    text(s,info.title,0.87,2.15,11.54,1.3,57,T.secondary,{serif:true,bold:true,align:'center'});
    // Minimal and audience-facing; never invent a sentimental slogan.
    if(info.subtitle) text(s,info.subtitle,1.64,3.98,10.05,1.03,21,T.primary,{align:'center'});
    label(s,'HỎI ĐÁP / THẢO LUẬN',2.98,5.99,7.38,'','center');
  }else{
    header(s,logical,info);
    if(ty==='cards'||ty==='summary'){
      const cards=info.cards, gap=0.24,w=(CONTENT_W-gap*(cards.length-1))/cards.length;
      const h=4.49,y=2.16;
      const names=[];
      for(let i=0;i<cards.length;i++){
        const x=M+i*(w+gap),def=i===0?'auto':'click';
        names.push(await cardPanel(s,n,m,`card${i+1}`,cards[i],x,y,w,h,def,used));
      }
      qa.card_rows.push({slide:n,shape_names:names,container_left:M,container_right:W-M,
        tolerance_in:0.065});
    }else if(ty==='contents'){
      // Repeated TOC visits are genuine PPTX slides but not additional
      // logical chapters. They use the same original raster and !!subject
      // names as the matching content photo, giving native Morph an anchor.
      const entries=info.entries||[];
      const columns=entries.length<=3?entries.length:3;
      const rows=Math.ceil(entries.length/columns);
      const gapX=0.20,gapY=0.21;
      const width=(CONTENT_W-gapX*(columns-1))/columns;
      const cellHeight=Math.min(2.15,(4.48-gapY*(rows-1))/rows);
      const areaTop=2.14;
      for(let i=0;i<entries.length;i++){
        const entry=entries[i],row=Math.floor(i/columns),col=i%columns;
        const inRow=Math.min(columns,entries.length-row*columns);
        const rowWidth=inRow*width+(inRow-1)*gapX;
        const rowX=M+(CONTENT_W-rowWidth)/2;
        const x=rowX+col*(width+gapX),y=areaTop+row*(cellHeight+gapY);
        shape(s,x,y,width,cellHeight,{fill:T.panel,name:'STATIC_toc'+i+'_panel'});
        const imageH=Math.max(0.66,Math.min(1.18,cellHeight-0.68));
        if(entry.image){
          const imageX=x+0.16,imageY=y+0.12;
          await putImage(s,n,entry.image,imageX,imageY,width-0.32,imageH,{
            morph_id:entry.morph_id||null,name:'STATIC_toc'+i+'_photo',
            alt:entry.title});used.push(entry.image);
        }
        const titleY=y+imageH+0.20;
        text(s,entry.title,x+0.18,titleY,width-0.36,
          Math.max(0.28,cellHeight-imageH-0.31),16,T.primary,
          {bold:true,align:'center',name:'STATIC_toc'+i+'_title'});
      }
    }else if(ty==='chart'){
      // Real, editable PowerPoint charts; data must be cited in chart_data.
      const d=info.chart_data||{};
      const kinds={bar:pptx.ChartType.bar,line:pptx.ChartType.line,pie:pptx.ChartType.pie};
      if(!kinds[d.kind])throw Error('Unsupported chart kind: '+d.kind);
      const series=d.series.map(v=>({name:v.name,labels:d.labels,values:v.values}));
      const opts={
        x:M+0.15,y:2.10,w:CONTENT_W-0.30,h:4.45,
        chartColors:[T.secondary,T.accent,T.muted,'A8B3D8'],
        showTitle:false,showLegend:d.series.length>1,
        legendColor:T.primary,legendFontFace:T.body_font,legendFontSize:11,
        catAxisLabelColor:T.text,valAxisLabelColor:T.text,
        catAxisLabelFontSize:11,valAxisLabelFontSize:11,
        showValue:d.kind==='pie',showPercent:d.kind==='pie',
        showCategoryName:false,showMarker:d.kind==='line',
        valGridLine:{color:'486170',transparency:65},
        showBorder:false,showShadow:false,
        showCatName:false,showSerName:false,
        showValAxisTitle:!!d.y_axis_title,valAxisTitle:d.y_axis_title||'',
      };
      s.addChart(kinds[d.kind],series,opts);
      const foot=d.caption||((d.unit?d.unit+' · ':'')+'Nguồn: '+d.source);
      text(s,foot,M+0.18,6.68,CONTENT_W-0.36,0.24,10.3,T.muted,
        {name:'STATIC_chart_source',align:'left'});

      const events=info.events,gap=0.22,w=(CONTENT_W-gap*(events.length-1))/events.length;
      rule(s,M+0.16,3.23,CONTENT_W-0.32,T.muted,50,'STRUCTURAL_timeline_axis');
      for(let i=0;i<events.length;i++){
        const event=events[i],x=M+i*(w+gap);
        const rv=m.pick(event.reveal||((i===0)?'auto':'click'),event.title);
        const nm=p=>objName(rv,`event${i+1}`,p);
        shape(s,x,2.72,w,3.58,{fill:T.panel,line:T.muted,lineTransparency:85,name:nm('frame')});
        label(s,event.badge||String(i+1),x+0.20,3.07,w-0.40,nm('badge'));
        text(s,event.title,x+0.20,3.80,w-0.40,0.50,18,T.primary,{bold:true,name:nm('title')});
        text(s,event.text,x+0.21,4.77,w-0.42,1.21,13,T.muted,{name:nm('text')});
      }
    }else if(ty==='split'||ty==='section'){
      const side=info.image_side||'right';
      const imageLeft=side==='left'?M:6.66;
      const textLeft=side==='left'?6.70:M;
      const imageWidth=5.75;
      if(info.image){
        const imgReveal=info.morph_id?'static':m.pick(info.image_reveal||'auto','Hình minh họa');
        const nm=p=>objName(imgReveal,'photo',p);
        shape(s,imageLeft,2.17,imageWidth,4.45,{fill:T.panel,name:nm('frame')});
        await putImage(s,n,info.image,imageLeft+0.13,2.30,imageWidth-0.26,4.19,{
          mode:info.image_mode||'preserve',decorative:!!info.decorative,
          morph_id:info.morph_id||null,name:nm('image')});used.push(info.image);
      }else{
        shape(s,imageLeft,2.17,imageWidth,4.45,{fill:T.panel});
        text(s,'“',imageLeft+1.58,2.14,2.5,2.52,95,T.secondary,{serif:true,align:'center'});
      }
      let bulletY=2.18;
      if((info.bullets||[]).length){
        const bs=info.bullets,number=bs.length,cellH=Math.min(1.33,4.26/number);
        for(let i=0;i<number;i++){
          const v=bs[i],rv=m.pick(v.reveal||((i===0)?'auto':'click'),v.title);
          const nm=p=>objName(rv,`bullet${i+1}`,p);
          const y=bulletY+i*(cellH+0.10);
          shape(s,textLeft,y,5.70,cellH,{fill:T.panel,name:nm('frame')});
          label(s,String(i+1).padStart(2,'0'),textLeft+0.17,y+0.19,0.46,nm('number'));
          text(s,v.title,textLeft+0.83,y+0.14,4.65,0.38,16.5,T.primary,{bold:true,name:nm('title')});
          text(s,v.text,textLeft+0.83,y+0.55,4.65,Math.max(.34,cellH-.68),11.3,T.muted,{name:nm('body')});
        }
      } else {
        text(s,info.quote||info.subtitle||info.title,textLeft+0.06,2.91,5.40,1.96,23,T.primary,{serif:true,bold:true});
      }
    }else if(ty==='diagram'){
      // A diagram's geometry must match its approved *semantic relation*.
      // Peers are equal; hierarchy has a parent; reciprocal shows two sides.
      // Never infer causal direction from a convenient 2x2 grid.
      const relationship=info.diagram_relationship||'peers';
      const x=M+0.33,w=CONTENT_W-0.66;
      const geo=planDiagram(relationship,(info.items||[]).length,{x,y:2.13,w,h:4.6});
      const rootRv=m.pick('auto','Chủ đề sơ đồ');
      const rootNm=p=>objName(rootRv,'diagramroot',p);
      if(relationship==='peers'){
        // Root is context, not an elevated parent of its peers.
        text(s,info.root,geo.root.x,geo.root.y,geo.root.w,geo.root.h,
          19.5,T.primary,{bold:true,align:'center',name:rootNm('heading')});
      }else{
        shape(s,geo.root.x,geo.root.y,geo.root.w,geo.root.h,
          {fill:T.panel,name:rootNm('panel')});
        text(s,info.root,geo.root.x+0.15,geo.root.y+0.1,
          geo.root.w-0.30,geo.root.h-0.20,
          19,T.primary,{bold:true,align:'center',name:rootNm('title')});
      }
      qa.centered_labels.push({slide:n,text:info.root,
        center_x:geo.root.x+geo.root.w/2,tolerance_in:0.055});
      const itemRv=m.pick('click','Các thành phần liên quan');
      const itemNm=(uid,part)=>objName(itemRv,uid,part);
      if(relationship==='reciprocal'){
        // The exchange and peers belong to the SAME timed entrance.
        text(s,info.group_label||'TÁC ĐỘNG QUA LẠI',
          geo.relLabel.x,geo.relLabel.y,geo.relLabel.w,geo.relLabel.h,
          12,T.secondary,{bold:true,align:'center',
          name:itemNm('exchange','title')});
        text(s,'↔',geo.arrow.x,geo.arrow.y,geo.arrow.w,geo.arrow.h,
          35,T.secondary,{align:'center',name:itemNm('exchange','arrow')});
        qa.centered_labels.push({slide:n,text:info.group_label||'TÁC ĐỘNG QUA LẠI',
          center_x:geo.relLabel.x+geo.relLabel.w/2,tolerance_in:0.06});
      }else{
        shape(s,geo.peerLabel.x,geo.peerLabel.y,geo.peerLabel.w,geo.peerLabel.h,
          {fill:T.secondary,name:itemNm('group','panel')});
        text(s,info.group_label||'CÁC THÀNH PHẦN',
          geo.peerLabel.x+0.12,geo.peerLabel.y+0.04,
          geo.peerLabel.w-0.24,geo.peerLabel.h-0.08,
          12.3,T.background,{bold:true,align:'center',
          name:itemNm('group','label')});
        qa.centered_labels.push({slide:n,
          text:info.group_label||'CÁC THÀNH PHẦN',
          center_x:geo.peerLabel.x+geo.peerLabel.w/2,tolerance_in:0.06});
      }
      const itemNames=[];
      (info.items||[]).forEach((labelText,i)=>{
        const t=geo.grid.tiles[i],uid='item'+(i+1);
        const frameName=itemNm(uid,'panel');
        shape(s,t.x,t.y,t.w,t.h,
          {fill:T.panel,line:T.muted,lineTransparency:82,name:frameName});
        text(s,labelText,t.x+0.13,t.y+0.08,t.w-0.26,t.h-0.16,
          15.1,T.primary,{bold:true,align:'center',name:itemNm(uid,'text')});
        itemNames.push(frameName);
      });
      qa.diagram_relationships.push({slide:n,relationship,
        item_shape_names:itemNames,root_shape_name:rootNm(
          relationship==='peers'?'heading':'panel'),
        peer_axis_x:geo.grid.centerX,tolerance_in:0.095});
      if(info.bottom){
        const bottomRv=m.pick('click',info.bottom);
        const bottomNm=p=>objName(bottomRv,'diagrambottom',p);
        shape(s,geo.bottom.x,geo.bottom.y,geo.bottom.w,geo.bottom.h,
          {fill:T.panel,name:bottomNm('panel')});
        text(s,info.bottom,geo.bottom.x+0.17,geo.bottom.y+0.07,
          geo.bottom.w-0.34,geo.bottom.h-0.14,16.5,T.secondary,
          {bold:true,align:'center',name:bottomNm('text')});
        qa.centered_labels.push({slide:n,text:info.bottom,
          center_x:geo.centerX,tolerance_in:0.06});
      }
      if(info.caption){
        label(s,info.caption,geo.caption.x,geo.caption.y,
          geo.caption.w,'','center');
        qa.centered_labels.push({slide:n,text:info.caption.toUpperCase(),
          center_x:geo.centerX,tolerance_in:0.06});
      }
    }else if(ty==='comparison'){
      const boxes=[info.left,info.right],xv=[M,6.81],w=5.79;
      boxes.forEach((v,i)=>{
        const rv=m.pick(v.reveal||(i?'click':'auto'),v.title);
        const nm=p=>objName(rv,`compare${i+1}`,p);
        shape(s,xv[i],2.28,w,4.27,{fill:T.panel,line:T.muted,lineTransparency:76,name:nm('panel')});
        label(s,v.badge||String(i+1),xv[i]+0.30,2.70,w-.60,nm('badge'));
        text(s,v.title,xv[i]+0.32,3.43,w-.64,0.71,25,T.primary,{serif:true,bold:true,name:nm('title')});
        text(s,v.text,xv[i]+0.32,4.71,w-.64,1.30,16,T.muted,{name:nm('description')});
      });
    }else if(ty==='quote'){
      if(info.image){
        await putImage(s,n,info.image,7.21,2.20,5.16,4.35,{alt:info.title});used.push(info.image);
      }
      const width=info.image?6.10:11.79;
      text(s,'“',M,2.04,1.2,1.21,74,T.secondary,{serif:true});
      text(s,info.quote||info.title,M,3.29,width,2.09,30,T.primary,{serif:true,bold:true});
      label(s,info.attribution||'TRÍCH DẪN',M,5.82,width);
    }else{throw Error(`Unsupported layout: ${ty}`);}
  }
  s.addNotes(sourceNotes(info,used,m));
  return {motion:m,used};
}

async function main(){
  const counts={auto:0,clicks:0,images:0};
  for(const visit of route.physical_slides){
    const i=visit.logical-1;
    const {motion,used}=await renderSlide(data.slides[i],visit.physical,visit.logical,visit.role);
    counts.auto += motion.click===0?0:1;
    counts.clicks += motion.click;
    counts.images += used.length;
  }
  const output=path.join(outDir,`${data.id}.base.pptx`);
  await pptx.writeFile({fileName:output});
  fs.writeFileSync(path.join(outDir,'qa-config.json'),JSON.stringify(qa,null,2));
  fs.writeFileSync(path.join(outDir,'image-audit.json'),JSON.stringify(imageAudit,null,2));
  fs.writeFileSync(path.join(outDir,'build-report.json'),JSON.stringify({id:data.id,title:data.title,
    logical_slides:data.slides.length,physical_slides:route.physical_count,
    revisit_count:route.revisit_count,tier,animation_mode:animationMode,
    requested_slide_count:data.requested_slide_count,
    clicks:counts.clicks,morph:route.morph_physical_destinations,
    asset_count:verified.length},null,2));
  console.log('BUILT',output,'logical',data.slides.length,'physical',route.physical_count,'clicks',counts.clicks);
}
main().catch(e=>{console.error('BUILD FAILED:',e.stack||e);process.exit(1)});
