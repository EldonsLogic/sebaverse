import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const base = 'http://127.0.0.1:5174';
const output = path.resolve('work/demo-browser');
fs.mkdirSync(output, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run'] });
const results = [];
const failures = [];

async function scan(page, label) {
  const result = await page.evaluate(() => {
    const problems = [];
    const visible = el => { const r=el.getBoundingClientRect(); const s=getComputedStyle(el); return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none'; };
    if (document.documentElement.scrollWidth > innerWidth + 1) problems.push('horizontal_overflow');
    if(document.querySelectorAll('main').length!==1 || document.querySelectorAll('h1').length!==1) problems.push('landmarks_or_heading');
    for(const input of document.querySelectorAll('input[type=radio]')) if(!input.closest('label') || !input.closest('fieldset')?.querySelector('legend')) problems.push('radio_label_or_legend');
    for(const el of document.querySelectorAll('button:not(:disabled), a, summary, label:has(input)')) {
      if(!visible(el)) continue;
      const r=el.getBoundingClientRect(); if(r.width+1e-6<44 || r.height+1e-6<44) problems.push('small_target:'+el.tagName);
    }
    const rgb = color => {
      const m=color.match(/[\d.]+/g); if(!m)return [0,0,0,0];
      const values=m.map(Number); return color.startsWith('color(srgb') ? values.map((v,i)=>i<3?v*255:v) : values;
    };
    const blend=(c,b)=>{const alpha=c.length===4?c[3]:1;return c.slice(0,3).map((v,i)=>v*alpha+b[i]*(1-alpha));};
    const luminance = c => c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
    let checkedText=0;
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    for(let node=walker.nextNode();node;node=walker.nextNode()) {
      const el=node.parentElement; if(!node.textContent.trim() || !el || !visible(el) || el.closest('.demo-sr-only,script,style')) continue;
      const style=getComputedStyle(el); if(style.opacity==='0')continue;
      let backgrounds=[[255,255,255]];
      const ancestry=[];for(let p=el;p;p=p.parentElement)ancestry.unshift(p);
      for(const p of ancestry){
        const ps=getComputedStyle(p); backgrounds=backgrounds.map(b=>blend(rgb(ps.backgroundColor),b));
        const stops=ps.backgroundImage.match(/rgba?\([^)]+\)|color\(srgb[^)]+\)/g);
        if(stops)backgrounds=backgrounds.flatMap(b=>stops.map(c=>blend(rgb(c),b)));
        for(const pseudo of ['::before','::after']){
          const overlay=getComputedStyle(p,pseudo); const color=rgb(overlay.backgroundColor);
          if(overlay.content!=='none' && color.length===4 && color[3]>0)backgrounds=backgrounds.flatMap(b=>[b,blend(color,b)]);
        }
        backgrounds=backgrounds.slice(0,32);
      }
      const color=rgb(style.color);
      const ratio=Math.min(...backgrounds.map(background=>{
        const foreground=blend(color,background); const a=luminance(foreground),b=luminance(background);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
      }));
      const large=parseFloat(style.fontSize)>=24 || (parseFloat(style.fontSize)>=18.66 && parseInt(style.fontWeight)>=700);
      checkedText++;if(ratio+1e-9<(large?3:4.5))problems.push('contrast:'+el.tagName+':'+ratio.toFixed(2));
    }
    return { problems:[...new Set(problems)],checkedText, stage:document.querySelector('main')?.dataset.demoStage,focus:document.activeElement?.id||document.activeElement?.tagName };
  });
  assert.deepEqual(result.problems, [], `${label} targeted accessibility check`);
  results.push({ label, ...result });
}
async function stage(page, expected) {
  await page.locator(`main[data-demo-stage="${expected}"]`).waitFor();
  await page.evaluate(async()=>{await document.fonts.ready; await new Promise(requestAnimationFrame);});
  if(expected!=='intro')assert.equal(await page.evaluate(()=>document.activeElement?.id),'demo-heading');
}
async function shot(page,width,label){await page.screenshot({path:path.join(output,`${width}-${label}.png`),fullPage:true});await scan(page,`${width}-${label}`);}
try {
  for (const [width,height] of [[360,900],[390,844],[768,1024],[1440,1080]]) {
    const context=await browser.newContext({viewport:{width,height},reducedMotion:'reduce'});
    const page=await context.newPage();page.setDefaultTimeout(12000);
    const unexpected=[],errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    await page.route('**/*',route=>{
      const url=new URL(route.request().url());
      if(url.origin!==base || url.pathname.startsWith('/api')){unexpected.push(url.origin+url.pathname);return route.abort();}
      return route.continue();
    });
    await page.addInitScript(()=>{
      window.__demoWrites=[];
      const original=Storage.prototype.setItem;
      Storage.prototype.setItem=function(key,value){window.__demoWrites.push(String(key));return original.call(this,key,value);};
    });
    await page.goto(base+'/demo/index.html',{waitUntil:'networkidle'});
    await stage(page,'intro'); assert.equal(await page.locator('html').getAttribute('dir'),'rtl');assert.equal(await page.locator('html').getAttribute('lang'),'ar');
    await shot(page,width,'intro');
    await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement?.className),'demo-skip');
    await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement?.id),'demo-main');
    await page.locator('input[value=visual]').check();await page.locator('[data-demo-primary]').click();await stage(page,'explanation');await shot(page,width,'explanation');
    await page.locator('[data-demo-source] summary').click();assert.equal(await page.locator('[data-demo-source]').getAttribute('open'),'');
    await page.locator('[data-demo-primary]').click();await stage(page,'guided');
    assert.equal(await page.locator('[data-demo-feedback]').count(),0);
    await page.locator('[data-demo-hint]').click();await page.locator('#demo-hint-text p').waitFor();assert.equal(await page.locator('#demo-hint-text').getAttribute('role'),'status');
    await shot(page,width,'guided-hint');
    await page.locator('input[value=guided-total]').check();await page.locator('[data-demo-primary]').click();await stage(page,'guided-feedback');await shot(page,width,'guided-feedback');
    await page.locator('[data-demo-primary]').click();await stage(page,'practice');assert.equal(await page.locator('[data-demo-hint], [data-demo-source], [data-demo-feedback]').count(),0);await shot(page,width,'practice');
    await page.locator('input[value=practice-size]').check();await page.locator('[data-demo-primary]').click();await stage(page,'practice-feedback');await shot(page,width,'practice-feedback');
    await page.locator('[data-demo-primary]').click();await stage(page,'summary');await shot(page,width,'summary');
    assert((await page.locator('main').innerText()).includes('استخدمت تلميح'));
    await page.locator('[data-demo-primary]').click();await stage(page,'intro');assert.equal(await page.locator('input:checked').count(),0);
    assert.deepEqual(await page.evaluate(()=>window.__demoWrites),[],'No browser storage writes');assert.deepEqual(await context.cookies(),[],'No added cookies');assert.deepEqual(unexpected,[],'No external/API requests');assert.deepEqual(errors,[],'No browser errors');
    await context.close();
  }
  const context=await browser.newContext({viewport:{width:390,height:844}});const page=await context.newPage();
  await page.goto(base+'/demo/index.html');await page.keyboard.press('Tab');await page.keyboard.press('Enter');
  // Complete and assert every transition using only native keyboard controls.
  const active=async selector=>assert(await page.evaluate(selector=>document.activeElement?.matches(selector),selector),'Keyboard focus: '+selector);
  const keys=async (...names)=>{for(const name of names)await page.keyboard.press(name);};
  await keys('Tab');await active('input[value=visual]');
  const outline=await page.locator('input[value=visual]').evaluate(el=>getComputedStyle(el.closest('label')).outlineWidth);
  assert(parseFloat(outline)>=3,'Visible radio focus');
  await keys('Space','Tab');await active('[data-demo-primary]');await keys('Enter');await stage(page,'explanation');
  await keys('Tab');await active('[data-demo-primary]');await keys('Enter');await stage(page,'guided');
  await keys('Tab','ArrowDown','Space');await active('input[value=guided-total]');
  await keys('Tab');await active('[data-demo-hint]');await keys('Space');await page.locator('#demo-hint-text p').waitFor();
  await keys('Tab');await active('[data-demo-primary]');await keys('Enter');await stage(page,'guided-feedback');
  await keys('Tab','Enter');await stage(page,'practice');
  await keys('Tab','ArrowDown','ArrowDown','Space');await active('input[value=practice-total]');
  await keys('Tab','Enter');await stage(page,'practice-feedback');
  await keys('Tab','Enter');await stage(page,'summary');assert((await page.locator('main').innerText()).includes('استخدمت تلميح'));
  await keys('Tab','Enter');await stage(page,'intro');assert.equal(await page.locator('input:checked').count(),0);
  for(const endpoint of ['/index.html','/src/app/App.tsx','/api/v1/health/'])assert.equal((await page.request.get(base+endpoint)).status(),404,'Isolated path '+endpoint);
  results.push({label:'keyboard_only_complete_reset_and_route_isolation',stage:'intro',focusVisible:true});
  await context.close();
} catch(error) {
  failures.push(error.message);
} finally {
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({status:failures.length?'fail':'pass',results,failures,scope:'Targeted semantic/contrast/target/reflow/focus checks; not full WCAG or learning efficacy certification.'},null,2)+'\n');
  await browser.close();
}
if(failures.length)throw new Error(failures.join('\n'));
console.log(JSON.stringify({status:'pass',checks:results.length,report:path.join(output,'report.json')}));
