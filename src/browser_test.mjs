import {chromium} from 'playwright';
import fs from 'node:fs';
const browser=await chromium.launch({executablePath:'/home/dev/.local/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const results=[];
for (const [name,width,height] of [['desktop',1440,1100],['mobile',390,844]]){
 const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8794/',{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>window.__R01_MODEL_READY,{timeout:180000});await page.waitForTimeout(2500);
 const info=await page.evaluate(()=>({triangles:window.__R01_TRIANGLES,frames:window.__R01_RENDER_FRAMES,overflow:document.documentElement.scrollWidth>innerWidth,width:innerWidth,canvasWidth:document.querySelector('canvas').clientWidth,canvasHeight:document.querySelector('canvas').clientHeight}));
 await page.screenshot({path:`build/reviews/website-${name}.png`,fullPage:true});
 await page.getByRole('button',{name:'Back',exact:true}).click();await page.waitForTimeout(800);
 const back=await page.locator('[data-view="back"]').getAttribute('class');
 await page.getByRole('button',{name:'Front',exact:true}).click();
 await page.getByRole('button',{name:'Reference',exact:true}).click();await page.waitForTimeout(600);
 const ref=await page.locator('#comparisonImage').getAttribute('src');
 results.push({name,...info,backControlWorks:back.includes('active'),referenceControlWorks:ref.includes('reference/rgirljk.png'),errors});await page.close();
}
await browser.close();fs.writeFileSync('build/browser-audit.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
