// Capture authoritative browser renders of every HTML slide before conversion.
import puppeteer from 'puppeteer';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const htmlPath = path.resolve(process.argv[2] ?? 'experiments/html-first/demo.html');
const output = path.resolve(process.argv[3] ?? 'experiments/html-first/dist/html-preview');
fs.mkdirSync(output, {recursive: true});

const browser = await puppeteer.launch({headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox']});
try {
  const page = await browser.newPage();
  await page.setViewport({width:1280,height:720, deviceScaleFactor:1});
  await page.goto(pathToFileURL(htmlPath).href, {waitUntil:'load'});
  const count = await page.$$eval('.slide', slides => slides.length);
  if (count !== 5) throw new Error('Expected exactly five HTML slides, found ' + count);
  for(let index=0; index<count; index++){
    await page.evaluate(index => {
      document.querySelectorAll('.slide').forEach((slide,i) => {
        slide.style.display = i===index ? 'flex' : 'none';
      });
    }, index);
    await page.screenshot({path:path.join(output,'slide-'+String(index+1).padStart(2,'0')+'.png'),
      clip:{x:0,y:0,width:1280,height:720}});
  }
  console.log('Captured',count,'browser slide screenshots in',output);
} finally {
  await browser.close();
}
