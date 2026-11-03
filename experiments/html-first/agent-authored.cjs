#!/usr/bin/env node
/**
 * Agent-authored PPTX transcription of demo.html.
 *
 * This file is generated for ONE deck by ChatGPT. It is intentionally NOT a
 * generic HTML converter or a fixed-layout presentation engine.
 *
 * Mapping decisions:
 * - HTML typography/cards/pipeline -> native PPTX text and shapes.
 * - HTML chart values -> a native editable PowerPoint chart (not bar pictures).
 * - HTML animation intent -> native groups by semantic objectName; a reusable
 *   OOXML serializer writes actual Fade/On Click in the next pipeline step.
 * - HTML gradient/decorative effects -> simple shapes or reduced static fill.
 * - Original content -> source notes and speaker notes, without invention.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const pptxgen = require('pptxgenjs');

const out = path.resolve(process.argv[2] || 'experiments/html-first/dist/agent-authored.base.pptx');
fs.mkdirSync(path.dirname(out), {recursive:true});
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE'; // 1280 x 720 @ 96 CSS pixels per inch
pptx.author = 'Chat Slide Studio - agent-generated A/B prototype';
pptx.subject = 'Native editable reconstruction of the HTML presentation';
pptx.title = 'HTML-first - Agent-authored Native PowerPoint';
pptx.lang = 'en-US';
pptx.theme = {headFontFace:'Arial', bodyFontFace:'Arial', lang:'en-US'};

const S = pptx.ShapeType;
const px = v => v/96;
const pt = v => v*.75;
const C = {
  dark:'0D182D', ink:'162338', white:'F9FCFF', paper:'F5F4EF',
  muted:'7E8BA0', slate:'5B6F87', mint:'8FDAC8', aqua:'249C92',
  paragraph:'4E637E', blue:'5470A3'
};
function text(slide, str, x, y, w, h, fontPx, color, extra={}){
  const options = {
    x:px(x),y:px(y),w:px(w),h:px(h),fontFace:'Arial',fontSize:pt(fontPx),
    color,margin:0,breakLine:false,align:'left',valign:'top',
    lineSpacingMultiple:1.0,transparency:0,
    ...extra
  };
  slide.addText(String(str),options);
}
function rect(slide,x,y,w,h,color,name,extra={}){
  slide.addShape(S.rect,{x:px(x),y:px(y),w:px(w),h:px(h),
    rectRadius:0,line:{color,width:0,transparency:100},
    fill:{color},objectName:name,...extra});
}
function round(slide,x,y,w,h,color,name,opts={}){
  slide.addShape(S.roundRect,{x:px(x),y:px(y),w:px(w),h:px(h),
    rectRadius:0.15,line:{color,width:0,transparency:100},
    fill:{color},objectName:name,...opts});
}
function circle(slide,x,y,w,color,trans,name){
  slide.addShape(S.ellipse,{x:px(x),y:px(y),w:px(w),h:px(w),
    fill:{color,transparency:trans},line:{color,transparency:100},
    objectName:name});
}
function page(num,kicker,dark=false){
  const s=pptx.addSlide();
  s.background = {color:dark?C.dark:C.paper};
  text(s,kicker,82,74,1030,29,17,dark?'91AED8':C.blue,
    {bold:true,charSpacing:2.5,objectName:'STATIC_slide'+num+'_kicker'});
  text(s,String(num).padStart(2,'0')+' / 05',1120,646,80,28,17,
    dark?'91AED8':C.muted,{bold:true,align:'right',
    objectName:'STATIC_slide'+num+'_number'});
  return s;
}
function notes(slide,body,cues=[]){
  const steps = cues.map((c,i)=>'Click '+(i+1)+': '+c).join('\n');
  slide.addNotes(body+'\n\n[Presenter cues]\n'+(steps||'No click required.')+
    '\n\n[Sources]\nOriginal self-contained HTML-first prototype; illustrative values only.');
}

// 1 - Editorial cover. CSS decoration is approximated with native shapes.
{
  const s=page(1,'HTML-FIRST / ENGINE EXPERIMENT 01',true);
  circle(s,895,7,350,'254965',45,'STATIC_cover_glow_top');
  circle(s,890,490,230,'1E6869',53,'STATIC_cover_glow_bottom');
  round(s,82,207,400,42,C.dark,'STATIC_cover_tag_bg',
    {line:{color:'6F9A9D',width:1.1,transparency:0}});
  text(s,'Editable PowerPoint, crafted from the DOM',102,217,367,24,16,
    'C8EFDF',{objectName:'STATIC_cover_tag'});
  text(s,'Ideas deserve',82,269,900,88,81,C.white,
    {bold:true,objectName:'AUTO_G0_cover_title1'});
  text(s,'better slides.',82,354,900,88,81,C.mint,
    {bold:true,objectName:'AUTO_G0_cover_title2'});
  text(s,'Exploring a single source for browser-quality design and native PowerPoint delivery.',
    82,465,700,86,25,'C2CFDF',{objectName:'STATIC_cover_supporting'});
  round(s,82,575,100,7,'80D4C2','STATIC_cover_accent_line');
  notes(s,'Introduce the HTML-first design experiment. The editorial title is native PowerPoint text. '+
    'The dark decorative shapes were authored natively rather than flattened.');
}

// 2 - Flexible cards converted by an agent into editable semantic groups.
{
  const s=page(2,'01 / DESIGN SYSTEM');
  text(s,'Good presentation design',82,123,1090,72,56,C.ink,
    {bold:true,objectName:'STATIC_s2_heading_1'});
  text(s,'starts with structure.',82,187,1090,72,56,C.ink,
    {bold:true,objectName:'STATIC_s2_heading_2'});
  const cards=[
    {i:'01',name:'One message',
     body:'Each slide answers a clear question instead of repeating a paragraph.'},
    {i:'02',name:'Visual hierarchy',
     body:'Spacing, typography and contrast explain what matters first.'},
    {i:'03',name:'Real editability',
     body:'Text and simple shapes should remain native PowerPoint objects.'}
  ];
  cards.forEach((c,i)=>{
    const x=82+i*(357+22),y=315;
    const prefix=i===0?'AUTO_G0_card1_':'CLICK_G'+i+'_card'+(i+1)+'_';
    round(s,x,y,357,270,'FFFFFF',prefix+'panel',{
      line:{color:'E2E7EE',width:.8},
      shadow:{type:'outer',color:'11203A',blur:2,angle:45,distance:1,opacity:.10}
    });
    text(s,c.i,x+31,y+34,300,28,19,C.aqua,
      {bold:true,objectName:prefix+'index'});
    text(s,c.name,x+31,y+98,301,42,28,C.ink,
      {bold:true,objectName:prefix+'title'});
    text(s,c.body,x+31,y+163,290,86,19,C.paragraph,
      {objectName:prefix+'copy'});
  });
  notes(s,'Explain the three design pillars. Each card consists of a background and text '+
    'objects sharing one timing group, preserving presentation pacing.',
    ['Reveal the Visual hierarchy card as a complete unit.',
     'Reveal the Real editability card as a complete unit.']);
}

// 3 - A structured process diagram, not an image of the web page.
{
  const s=page(3,'02 / PRODUCTION PIPELINE');
  text(s,'Design once. Deliver twice.',82,132,1100,79,56,C.ink,
    {bold:true,objectName:'STATIC_s3_heading'});
  const blocks=[
    {x:82,tag:'INPUT',title:'HTML & CSS',
      copy:'Flexible grids, typography and semantics in a browser.'},
    {x:457,tag:'COMPILER',title:'DOM → shapes',
      copy:'Measure layout, map editable content and motion.'},
    {x:832,tag:'OUTPUT',title:'Native PPTX',
      copy:'Reviewable, reusable and editable presentation files.'}
  ];
  blocks.forEach((b,i)=>{
    round(s,b.x,290,310,191,'E9F0F7','STATIC_process'+i+'_panel',{
      line:{color:'D2E2F3',width:1.25}
    });
    round(s,b.x+32,321,b.tag==='COMPILER'?126:88,34,'E2F6F0',
      'STATIC_process'+i+'_tag_bg');
    text(s,b.tag,b.x+45,330,125,19,17,'0F766E',
      {bold:true,objectName:'STATIC_process'+i+'_tag'});
    text(s,b.title,b.x+32,367,260,39,29,C.ink,
      {bold:true,objectName:'STATIC_process'+i+'_title'});
    text(s,b.copy,b.x+32,411,259,70,19,'49617A',
      {objectName:'STATIC_process'+i+'_copy'});
  });
  text(s,'→',404,366,44,54,38,C.aqua,
      {bold:true,align:'center',objectName:'STATIC_process_arrow1'});
  text(s,'→',779,366,44,54,38,C.aqua,
      {bold:true,align:'center',objectName:'STATIC_process_arrow2'});
  round(s,82,555,1110,84,'EAF0F6','STATIC_s3_quote_bg');
  rect(s,82,555,6,84,C.aqua,'STATIC_s3_quote_line');
  text(s,'The browser is the design surface; PowerPoint remains the deliverable.',
      110,578,1015,52,25,'35516D',{objectName:'STATIC_s3_quote'});
  notes(s,'Explain the dual output workflow: browser design, semantic mapping and native PPTX. '+
    'All flow boxes and arrows are editable text and shapes.');
}

// 4 - IMPORTANT: preserve the actual data as an editable PowerPoint chart.
{
  const s=page(4,'03 / DATA STORYTELLING');
  text(s,'Numbers should communicate.',82,126,1100,83,56,C.ink,
    {bold:true,objectName:'STATIC_s4_heading'});
  text(s,'Illustrative values only. Not actual business performance.',
    82,208,1050,42,21,C.slate,{objectName:'STATIC_s4_disclaimer'});
  const series=[{name:'Illustrative performance',labels:['Discover','Explore','Design','Deliver'],
    values:[24,42,58,68]}];
  s.addChart(pptx.ChartType.bar,series,{
    x:px(82),y:px(293),w:px(1045),h:px(310),
    barDir:'col',grouping:'clustered',gapWidthPct:75,
    showTitle:false,showLegend:false,
    chartColors:['188EAB'],varyColors:false,
    showValue:true,dataLabelPosition:'outEnd',
    dataLabelFormatCode:'0',dataLabelColor:'143753',dataLabelFormatCodeSourceLinked:false,
    dataLabelFormatCode:'0',dataLabelFormatCodeSourceLinked:false,
    dataLabelFontFace:'Arial',dataLabelFontSize:16,
    showCatName:false,
    catAxisLabelFontFace:'Arial',catAxisLabelFontSize:16,catAxisLabelColor:'48627E',
    showValAxis:false,showCatAxis:true,
    valAxisMinVal:0,valAxisMaxVal:75,valAxisMajorUnit:15,
    showMarker:false,showBorder:false,
    showShadow:false,showSerName:false,
    showValue:true,
    valGridLine:{color:'F5F4EF',transparency:100},
    showPlotArea:false,showChartArea:false,
    showZeroLine:false,
    layout:{x:.02,y:.0,w:.96,h:.95},
    objectName:'STATIC_s4_native_editable_chart'
  });
  text(s,'Original HTML used decorative bars. This PPTX uses a real editable chart data series.',
    82,636,1070,32,18,'718398',
    {objectName:'STATIC_s4_chart_note'});
  notes(s,'These are example numbers: Discover 24, Explore 42, Design 58, Deliver 68. '+
    'They are NOT real business metrics. Unlike HTML bar divs, this is an editable '+
    'PowerPoint chart object with numerical series. [Chart data] 24, 42, 58, 68.');
}

// 5 - Intent-driven native PowerPoint Fade/On Click groups.
{
  const s=page(5,'04 / QUALITY GATE',true);
  circle(s,897,4,350,'254965',45,'STATIC_end_glow');
  text(s,'From pixels',82,257,1020,94,96,C.white,
    {bold:true,objectName:'AUTO_G0_s5_heading1'});
  text(s,'to precision.',82,350,1020,94,96,C.mint,
    {bold:true,objectName:'AUTO_G0_s5_heading2'});
  text(s,'A real proof of concept must measure visual differences, native shape editability and PowerPoint animation separately.',
    82,478,784,107,25,'C7D4E2',
    {objectName:'CLICK_G1_s5_supporting_text'});
  round(s,82,607,538,58,'8ADAC6','CLICK_G2_s5_cta_panel');
  text(s,'Prototype · Not yet a production exporter',108,621,500,31,
    23,'16394C',{bold:true,objectName:'CLICK_G2_s5_cta_text'});
  notes(s,'Conclude by distinguishing editable structure, static visual fidelity, '+
    'and actual Microsoft PowerPoint playback evidence.',
    ['Reveal the need for separate visual, editability and motion evidence.',
     'Show the prototype status callout.']);
}
pptx.writeFile({fileName:out});
console.log('AGENT-AUTHORED NATIVE PPTX WROTE',out);
