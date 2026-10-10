import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { brotliDecompressSync } from 'node:zlib';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { chromium as playwright } from '@playwright/test';
import chromium from '@sparticuz/chromium';

const base = process.env.BASE_URL || 'http://127.0.0.1:3000';
// The minimal sandbox lacks NSS. Use the libraries bundled by this pinned
// Chromium package, without an OS package install or a third-party download.
await fs.mkdir('.cache/chromium-libs',{recursive:true});
const libsArchive = await fs.readFile('node_modules/@sparticuz/chromium/bin/al2023.tar.br');
await fs.writeFile('.cache/chromium-libs/al2023.tar',brotliDecompressSync(libsArchive));
execFileSync('tar',['-xf','.cache/chromium-libs/al2023.tar','-C','.cache/chromium-libs']);
const libraryPath = path.resolve('.cache/chromium-libs/lib');
const executablePath = await chromium.executablePath();
const browser = await playwright.launch({ executablePath, args: chromium.args, headless: true, env: {...process.env, LD_LIBRARY_PATH: `${libraryPath}:${process.env.LD_LIBRARY_PATH || ''}`}  });
const context = await browser.newContext({ viewport: {width:1440,height:1000}, acceptDownloads:true });
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
await fs.mkdir('.cache/browser',{recursive:true});
try {
  const health = await (await fetch(`${base}/api/health`)).json();
  assert.equal(health.mapAvailable,true); assert.equal(health.downloadAvailable,true);
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.mapReview?.ready,undefined,{timeout:60000});
  const quality = await (await fetch(`${base}/data/quality.json`)).json();
  assert.equal(await page.locator('#feature-count').textContent(),new Intl.NumberFormat('en').format(quality.featureCount));
  assert.equal(await page.locator('#source-notice').isVisible(),false);
  assert.equal(await page.locator('[data-mode="clean"]').getAttribute('aria-pressed'),'true');
  const blackPixels = () => page.evaluate(()=>{
    const c=document.querySelector('#map'), d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
    let n=0;for(let i=0;i<d.length;i+=4) if(d[i+3]>240 && Math.max(d[i],d[i+1],d[i+2])<70) n++;
    return n;
  });
  await page.waitForTimeout(200);
  assert.equal(await blackPixels(),0,'Clean canvas contains opaque black/near-black pixels');
  await page.screenshot({path:'.cache/browser/desktop.png',fullPage:true});

  const before = await page.locator('#zoom-label').textContent();
  await page.locator('#zoom-in').click(); await page.waitForTimeout(100);
  assert.notEqual(await page.locator('#zoom-label').textContent(),before);
  await page.locator('#fit').click();
  await page.locator('[data-region="1"]').click();
  await page.locator('#map').click({position:{x:280,y:230}});
  // The anomaly queue deterministically selects a known body regardless of fit.
  await page.locator('#next-issue').click();
  assert.match(await page.locator('#inspect-title').textContent(),/^Polygon /);
  assert.ok((await page.locator('#issue-position').textContent()).includes('flagged bodies'));
  await page.locator('#compare-selection').click();
  assert.equal(await page.locator('#source-notice').isVisible(),true);
  assert.equal(await page.locator('#compare-control').isVisible(),true);
  await page.locator('#compare-position').fill('72');
  assert.equal(await page.locator('#compare-position').inputValue(),'72');
  await page.locator('[data-mode="source"]').click();
  await page.locator('#fit').click();await page.waitForTimeout(200);
  assert.ok(await blackPixels()>0,'Source comparison should retain the original annotations');
  await page.locator('[data-mode="clean"]').click();
  await page.waitForTimeout(150);
  assert.equal(await blackPixels(),0);

  await page.locator('#legend-search').fill('basalt');
  assert.ok(await page.locator('.unit').count()>=2);
  await page.locator('.unit').first().click();
  assert.equal(await page.locator('#clear-highlight').isVisible(),true);
  await page.locator('#clear-highlight').click();
  await page.locator('#legend-search').fill('');
  await page.locator('#show-contacts').uncheck();
  await page.waitForTimeout(100);assert.equal(await blackPixels(),0);
  await page.locator('#show-contacts').check();
  const downloadPromise = page.waitForEvent('download');
  await page.locator('.download').click();
  const download = await downloadPromise;
  assert.equal(download.suggestedFilename(),'NGSA_geology_v5.zip');
  assert.equal(await download.failure(),null);

  await page.setViewportSize({width:390,height:844});
  await page.locator('#fit').click();await page.waitForTimeout(200);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth),false,'Mobile page overflows horizontally');
  assert.equal(await page.evaluate(()=>document.querySelector('.workspace').scrollWidth>document.querySelector('.workspace').clientWidth+1),false,'Mobile map is clipped inside its grid');
  await page.evaluate(()=>{document.querySelector('.workspace').scrollLeft=0;});
  await page.screenshot({path:'.cache/browser/mobile.png',fullPage:false,timeout:60000});
  assert.equal(await page.locator('.download').isVisible(),true);
  assert.deepEqual(errors,[]);
  console.log('PASS: real Chromium desktop/mobile rendering, clean-map black-pixel check, source distinction, inspection, anomaly navigation, comparison, zoom, legend, contact toggle, ZIP download.');
} finally { await browser.close(); }
