#!/usr/bin/env node
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, copyFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';

const videoArg = process.argv[2];
const outputArg = process.argv[3] || 'docs/screenshots';
if (!videoArg) {
  console.error('Usage: node scripts/capture-readme-frames.mjs <video.mp4> [output-dir]');
  process.exit(2);
}

const video = resolve(videoArg);
const output = resolve(outputArg);
await mkdir(output, { recursive: true });
const work = await mkdtemp(join(tmpdir(), 'lyricvid-readme-'));
const servedVideo = join(work, basename(video));
await copyFile(video, servedVideo);

const port = 39000 + Math.floor(Math.random() * 1000);
const server = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1', '--directory', work], {
  stdio: 'ignore',
});

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await sleep(800);

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const src = `http://127.0.0.1:${port}/${encodeURIComponent(basename(video))}`;
await page.setContent(`<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#05070a;height:100%;display:grid;place-items:center}
.wrap{width:1280px;box-shadow:0 20px 80px rgba(0,0,0,.65)}
video{display:block;width:1280px;height:720px;background:#000}
</style></head><body><div class="wrap"><video id="v" src="${src}" preload="auto" muted playsinline></video></div></body></html>`);

await page.waitForFunction(() => {
  const v = document.querySelector('#v');
  return v && Number.isFinite(v.duration) && v.duration > 0;
}, { timeout: 30000 });

const duration = await page.$eval('#v', (v) => v.duration);
const captures = [
  ['intro.png', Math.min(1.5, Math.max(0.1, duration * 0.03))],
  ['middle.png', duration * 0.5],
  ['outro.png', Math.max(0.1, duration - 2.0)],
];

for (const [name, t] of captures) {
  await page.$eval('#v', (v, time) => new Promise((resolveSeek) => {
    const done = () => { v.removeEventListener('seeked', done); resolveSeek(); };
    v.addEventListener('seeked', done, { once: true });
    v.currentTime = Math.max(0, Math.min(time, v.duration - 0.05));
  }), t);
  await sleep(200);
  const el = page.locator('.wrap');
  await el.screenshot({ path: join(output, name) });
  console.log(`✓ ${name} @ ${t.toFixed(2)}s`);
}

await browser.close();
server.kill('SIGTERM');
await rm(work, { recursive: true, force: true });
console.log(`✓ README frames written to ${output}`);
