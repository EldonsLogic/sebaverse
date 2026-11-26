import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import zlib from 'node:zlib';

const root = path.resolve(import.meta.dirname, '../..');
const dist = path.join(root, 'web/dist');
const marker = 'SEBAVERSE_LOCAL_TEACHING_DEMO_ONLY';
const files = [];
function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(full);
    else files.push(full);
  }
}
walk(dist);
assert(fs.existsSync(path.join(dist, 'index.html')), 'Default app build missing');
assert(!fs.existsSync(path.join(dist, 'demo')), 'Demo entry leaked into default build');
for (const file of files.filter(file => /\.(js|css|html)$/.test(file))) {
  assert(!fs.readFileSync(file, 'utf8').includes(marker), 'Demo module leaked into default build');
}
const scripts = files.filter(file => /\.(js|css)$/.test(file));
const gzipBytes = scripts.reduce((total, file) => total + zlib.gzipSync(fs.readFileSync(file)).length, 0);
console.log(JSON.stringify({ defaultBuildExcludesDemo: true, scriptStyleGzipBytes: gzipBytes, scope: 'Default app artifact inspection; not a browser or demo bundle measurement.' }));
