import { build } from '../../web/node_modules/vite/dist/node/index.js';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import assert from 'node:assert/strict';

const root = path.resolve(import.meta.dirname, '../..');
const web = path.join(root, 'web');
const out = path.join(root, 'work/demo-optimized-measurement');
await build({ root: web, configFile: false, envDir: false, logLevel: 'error', build: { outDir: out, emptyOutDir: true, rollupOptions: { input: path.join(web, 'demo/index.html') } } });
let scriptStyleGzipBytes = 0;
for (const name of fs.readdirSync(path.join(out, 'assets'))) if (/\.(js|css)$/.test(name)) scriptStyleGzipBytes += zlib.gzipSync(fs.readFileSync(path.join(out, 'assets', name))).length;
assert(scriptStyleGzipBytes <= 200_000, 'Optimized demonstration exceeds script/style budget');
const fonts = ['Rubik-VF.ttf','Alexandria-VF.ttf'].map(name=>({name,bytes:fs.statSync(path.join(web,'public/brand/fonts',name)).size}));
const report = { scriptStyleGzipBytes, maxBytes: 200_000, fonts, scope: 'Disposable optimized demo measurement, not development-server transfer or production deployment. Existing TTFs are not subsetted WOFF2.' };
fs.mkdirSync(path.join(root, 'work/demo-browser'), { recursive: true });
fs.writeFileSync(path.join(root, 'work/demo-browser/bundle-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
