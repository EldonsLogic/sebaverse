import { chromium } from 'playwright';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base=process.env.SEBAVERSE_BASE_URL||'http://127.0.0.1:8010';
const output=process.env.SEBAVERSE_BROWSER_OUTPUT||'outputs/f2-local-skeleton';
fs.mkdirSync(output,{recursive:true});
const executable=process.env.SEBAVERSE_BROWSER_EXECUTABLE;
const browser=await chromium.launch({headless:true,...(executable?{executablePath:executable}:{})});
const results=[];
const routeHeadings={'/materials':'موادي','/practice':'التدريب','/progress':'تقدّمي','/':'نبدأ من اللي'};
async function settledRoute(page,route){
 await page.waitForFunction(({route,text})=>{
  const h=document.querySelector('main h1');
  const current=document.querySelector('nav a[aria-current="page"]');
  return location.pathname===route && h?.textContent?.includes(text) && current?.getAttribute('href')===route && document.activeElement?.id==='main-content';
 },{route,text:routeHeadings[route]});
 await page.evaluate(async()=>{await document.fonts.ready;for(let n=0;n<6;n++)await new Promise(requestAnimationFrame);});
}

try {
 for(const [name,width,height] of [['desktop',1440,1050],['mobile',390,844]]){
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(20000);
  console.log('Checking '+name);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const badResponses=[];page.on('response',r=>{if(r.status()>=400&&r.url().startsWith(base))badResponses.push({status:r.status(),url:r.url()});});
  await page.goto(base,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('html').getAttribute('dir'),'rtl');
  assert.equal(await page.locator('html').getAttribute('lang'),'ar');
  await page.locator('.brand-logo').waitFor({state:'visible'});
  assert.equal(await page.locator('.brand-logo').evaluate(el=>getComputedStyle(el).transform),'none');
  assert.equal(await page.locator('main h1').count(),1);
  await page.keyboard.press('Tab');
  const first=await page.evaluate(()=>({href:document.activeElement?.getAttribute('href'),text:document.activeElement?.textContent}));
  assert.equal(first.href,'#main-content','First focus must be the skip link');
  for(const route of ['/materials','/practice','/progress','/']){
   const nav=page.locator('nav[aria-label="التنقّل الرئيسي"]');
   await nav.locator(`a[href="${route}"]`).click();
   await settledRoute(page,route);
   assert.equal(await page.locator('main h1').count(),1);
   assert.ok(await page.title());
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'No horizontal overflow');
  }
  const inputs=await page.locator('input[type=file],input[type=password]').count();assert.equal(inputs,0,'No premature upload/account capture');
  await page.evaluate(()=>{history.pushState({},'', '/not-a-route');dispatchEvent(new PopStateEvent('popstate'));});
  await page.waitForFunction(()=>location.pathname==='/not-a-route'&&document.querySelector('main h1')?.textContent?.includes('نرجع لمساحة التعلّم؟')&&document.title.includes('غير موجودة'));
  assert.ok((await page.title()).includes('غير موجودة'));
  await page.locator('nav a[href="/"]').click();await settledRoute(page,'/');
  await page.locator('.page-footer').scrollIntoViewIfNeeded();
  await page.evaluate(async()=>{scrollTo(0,0);for(let n=0;n<6;n++)await new Promise(requestAnimationFrame);});
  const documentHeight=await page.evaluate(()=>Math.max(document.documentElement.scrollHeight,document.body.scrollHeight));
  const png=await page.screenshot({path:`${output}/${name}.png`,fullPage:true});
  const imageHeight=png.readUInt32BE(20);
  assert.ok(imageHeight>=documentHeight,'Full-page capture must include settled document, not stale route bounds');
  assert.deepEqual(errors,[],'No uncaught UI exceptions');assert.deepEqual(badResponses,[],'No missing application assets');
  const live=await page.request.get(`${base}/api/v1/health/`);assert.equal(live.status(),200);assert.deepEqual(await live.json(),{status:'ok'});
  const missing=await page.request.get(`${base}/api/no-such-route/`);assert.equal(missing.status(),404);assert.ok((missing.headers()['content-type']||'').includes('application/json'));
  results.push({viewport:name,width,height,routes:4,rtl:true,skip_link:true,overflow:false,ui_errors:errors.length,asset_failures:badResponses.length,health:200,unknown_api:404,client_not_found:true,main_focus:true,document_height:documentHeight,image_height:imageHeight});
  await page.close();
 }
 const report={date:new Date().toISOString(),browser:browser.version(),tool:'playwright1.62.1',base_url:base,checks:results,scope:'Local authored empty shell only; no learner/model/data/API feature or accessibility certification'};
 fs.writeFileSync(`${output}/browser-report.json`,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
} finally {await browser.close();}
