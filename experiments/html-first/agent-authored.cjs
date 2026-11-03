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
const portable = process.argv.includes('--portable'); // Visible/editable in cross-app imports, no native Office chart.
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
function addClippedGlows(slide,includeBottom){
  // Decorative SVG only, clipped to the 16:9 canvas. All words and graphics
  // carrying meaning remain native editable PowerPoint objects.
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">' +
    '<circle cx="1175" cy="80" r="265" fill="#254965" fill-opacity=".60"/>' +
    (includeBottom ? '<circle cx="1032.5" cy="712.5" r="167.5" fill="#1E6869" fill-opacity=".45"/>' : '') +
    '</svg>';
  slide.addImage({data:'data:image/svg+xml;base64,'+Buffer.from(svg).toString('base64'),
    x:0,y:0,w:px(1280),h:px(720),objectName:'STATIC_clipped_decorative_glows'});
}
function addPortableDecor(slide,includeBottom){
  // Plain PowerPoint ellipses only. Avoid SVG/image fallback parts, whose
  // imports can become broken pictures in Google Slides or Keynote.
  slide.addShape(S.ellipse,{
    x:px(946), y:px(0), w:px(324), h:px(292),
    fill:{color:'254965',transparency:42}, line:{color:'254965',transparency:100},
    objectName:'STATIC_portable_upper_decor'
  });
  if(includeBottom) slide.addShape(S.ellipse,{
    x:px(897), y:px(566), w:px(294), h:px(150),
    fill:{color:'1E6869',transparency:53}, line:{color:'1E6869',transparency:100},
    objectName:'STATIC_portable_lower_decor'
  });
}
function page(num,kicker,dark=false){
  const s=pptx.addSlide();
  s.background = {color:dark?C.dark:C.paper};
  if(dark) (portable ? addPortableDecor(s,num===1) : addClippedGlows(s,num===1));
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
  round(s,82,179,400,42,C.dark,'STATIC_cover_tag_bg',
    {line:{color:'6F9A9D',width:1.1,transparency:0}});
  text(s,'Editable PowerPoint, crafted from the DOM',102,189,367,24,16,
    'C8EFDF',{objectName:'STATIC_cover_tag'});
  text(s,'Ideas deserve',82,237,900,88,81,C.white,
    {bold:true,objectName:'AUTO_G0_cover_title1'});
  text(s,'better slides.',82,322,900,88,81,C.mint,
    {bold:true,objectName:'AUTO_G0_cover_title2'});
  text(s,'Exploring a single source for browser-quality design and native PowerPoint delivery.',
    82,428,660,86,25,'C2CFDF',{objectName:'STATIC_cover_supporting'});
  round(s,82,545,100,7,'80D4C2','STATIC_cover_accent_line');
  notes(s,'Introduce the HTML-first design experiment. The editorial title is native PowerPoint text. '+
    'The dark decorative shapes were authored natively rather than flattened.');
}

// 2 - Flexible cards converted by an agent into editable semantic groups.
{
  const s=page(2,'01 / DESIGN SYSTEM');
  text(s,'Good presentation design',82,96,1090,72,56,C.ink,
    {bold:true,objectName:'STATIC_s2_heading_1'});
  text(s,'starts with structure.',82,160,1090,72,56,C.ink,
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
    const x=82+i*(357+22),y=291;
    const prefix=i===0?'AUTO_G0_card1_':'CLICK_G'+i+'_card'+(i+1)+'_';
    round(s,x,y,357,270,'FFFFFF',prefix+'panel',{
      line:{color:'E2E7EE',width:.8},
      shadow:{type:'outer',color:'11203A',blur:2,angle:45,distance:1,opacity:.10}
    });
    text(s,c.i,x+31,y+34,300,28,19,C.aqua,
      {bold:true,objectName:prefix+'index'});
    text(s,c.name,x+31,y+90,301,42,28,C.ink,
      {bold:true,objectName:prefix+'title'});
    text(s,c.body,x+31,y+155,290,86,19,C.paragraph,
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
  text(s,'Design once. Deliver twice.',82,100,1100,79,56,C.ink,
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
    round(s,b.x,260,310,191,'E9F0F7','STATIC_process'+i+'_panel',{
      line:{color:'D2E2F3',width:1.25}
    });
    round(s,b.x+32,291,b.tag==='COMPILER'?126:88,34,'E2F6F0',
      'STATIC_process'+i+'_tag_bg');
    text(s,b.tag,b.x+45,300,125,19,17,'0F766E',
      {bold:true,objectName:'STATIC_process'+i+'_tag'});
    text(s,b.title,b.x+32,337,260,39,29,C.ink,
      {bold:true,objectName:'STATIC_process'+i+'_title'});
    text(s,b.copy,b.x+32,381,259,70,19,'49617A',
      {objectName:'STATIC_process'+i+'_copy'});
  });
  text(s,'→',404,336,44,54,38,C.aqua,
      {bold:true,align:'center',objectName:'STATIC_process_arrow1'});
  text(s,'→',779,336,44,54,38,C.aqua,
      {bold:true,align:'center',objectName:'STATIC_process_arrow2'});
  round(s,82,525,1110,84,'EAF0F6','STATIC_s3_quote_bg');
  rect(s,82,525,6,84,C.aqua,'STATIC_s3_quote_line');
  text(s,'The browser is the design surface; PowerPoint remains the deliverable.',
      110,548,1015,52,25,'35516D',{objectName:'STATIC_s3_quote'});
  notes(s,'Explain the dual output workflow: browser design, semantic mapping and native PPTX. '+
    'All flow boxes and arrows are editable text and shapes.');
}

// 4 - One source dataset, two implementations.
// Native PowerPoint mode retains an Excel-backed Chart object.
// Portable mode intentionally uses only editable PPTX shapes and text; Keynote
// and Google Slides cannot be trusted to import the Office chart data object.
{
  const s=page(4,'03 / DATA STORYTELLING');
  text(s,'Numbers should communicate.',82,100,1100,83,56,C.ink,
    {bold:true,objectName:'STATIC_s4_heading'});
  text(s,'Illustrative values only. Not actual business performance.',
    82,182,1050,42,21,C.slate,{objectName:'STATIC_s4_disclaimer'});
  const chartData=[
    {label:'Discover',value:24,height:113},
    {label:'Explore',value:42,height:193},
    {label:'Design',value:58,height:265},
    {label:'Deliver',value:68,height:303}
  ];
  if(portable){
    const bottom=520;
    chartData.forEach((d,i)=>{
      const x=111+i*239, y=bottom-d.height;
      // Each bar, value and category is a genuine editable PowerPoint object.
      // No chart XML and NO rasterized slide/component can go missing on import.
      round(s,x,y,157,d.height,'188EAB','STATIC_s4_bar_'+i,
        {line:{color:'188EAB',transparency:100}});
      text(s,String(d.value),x,y-43,157,38,31,'143753',
        {bold:true,align:'center',objectName:'STATIC_s4_value_'+i});
      text(s,d.label,x-13,bottom+14,183,35,21,'48627E',
        {bold:true,align:'center',objectName:'STATIC_s4_label_'+i});
    });
  }else{
    const series=[{name:'Illustrative performance',
      labels:chartData.map(x=>x.label),values:chartData.map(x=>x.value)}];
    s.addChart(pptx.ChartType.bar,series,{
      x:px(82),y:px(255),w:px(1045),h:px(310),
      barDir:'col',grouping:'clustered',gapWidthPct:75,
      showTitle:false,showLegend:false,
      chartColors:['188EAB'],varyColors:false,
      showValue:true,dataLabelPosition:'outEnd',dataLabelColor:'143753',
      dataLabelFormatCode:'0',dataLabelFormatCodeSourceLinked:false,
      dataLabelFontFace:'Arial',dataLabelFontSize:16,
      showCatName:false,
      catAxisLabelFontFace:'Arial',catAxisLabelFontSize:16,catAxisLabelColor:'48627E',
      showValAxis:false,showCatAxis:true,
      valAxisMinVal:0,valAxisMaxVal:75,valAxisMajorUnit:15,
      showMarker:false,showBorder:false,showShadow:false,showSerName:false,
      valGridLine:{color:'F5F4EF',transparency:100},
      showPlotArea:false,showChartArea:false,showZeroLine:false,
      layout:{x:.02,y:.0,w:.96,h:.95},
      objectName:'STATIC_s4_native_editable_chart'
    });
  }
  text(s,'Illustrative values for chart conversion and editability testing.',
    82,604,1070,32,18,'718398',
    {objectName:'STATIC_s4_chart_note'});
  notes(s,'Illustrative data: Discover 24, Explore 42, Design 58, Deliver 68. '+
    (portable ?
      'Portable chart: each bar, value and label is individually editable in slide apps. '+
      'This is not a native linked Excel chart: edit each bar/number manually.' :
      'PowerPoint-specific chart has a linked data series; third-party import may render incorrectly.')+
    ' Never present these numbers as actual business results.');
}

// 5 - Intent-driven native PowerPoint Fade/On Click groups.
{
  const s=page(5,'04 / QUALITY GATE',true);
  text(s,'From pixels',82,181,1020,94,96,C.white,
    {bold:true,objectName:'AUTO_G0_s5_heading1'});
  text(s,'to precision.',82,274,1020,94,96,C.mint,
    {bold:true,objectName:'AUTO_G0_s5_heading2'});
  text(s,'A real proof of concept must measure visual differences, native shape editability and PowerPoint animation separately.',
    82,401,784,107,25,'C7D4E2',
    {objectName:'CLICK_G1_s5_supporting_text'});
  round(s,82,534,538,58,'8ADAC6','CLICK_G2_s5_cta_panel');
  text(s,'Prototype · Not yet a production exporter',108,548,500,31,
    23,'16394C',{bold:true,objectName:'CLICK_G2_s5_cta_text'});
  notes(s,'Conclude by distinguishing editable structure, static visual fidelity, '+
    'and actual Microsoft PowerPoint playback evidence.',
    ['Reveal the need for separate visual, editability and motion evidence.',
     'Show the prototype status callout.']);
}
pptx.writeFile({fileName:out});
console.log('AGENT-AUTHORED '+(portable?'PORTABLE SHAPES':'NATIVE CHART')+' PPTX WROTE',out);
