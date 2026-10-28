// Renders reel.html frame by frame with Playwright.
//   node capture.js video <out.mp4>          -> silent 30fps H.264 video
//   node capture.js stills <dir> 1.2,5,9.8   -> PNG stills at the given seconds
//   node capture.js cover <out.png>           -> reel cover from cover.html
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ROOT = __dirname;
const FPS = 30, DURATION = 29.0;

function loadData() {
  const words = JSON.parse(fs.readFileSync(path.join(ROOT, "data/words.json"), "utf8"));
  const reviews = JSON.parse(fs.readFileSync(path.join(ROOT, "data/reviews.json"), "utf8"));
  const previews = fs.readdirSync(path.join(ROOT, "previews"))
    .filter(f => /\.(png|jpe?g|webp)$/i.test(f)).sort().map(f => "previews/" + f);
  return { words, reviews, previews };
}

async function open() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(ROOT, "reel.html"));
  await page.evaluate(d => window.boot(d), loadData());
  return { browser, page };
}

(async () => {
  const [mode, out, list] = process.argv.slice(2);
  if (mode === "cover") {
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await page.goto("file://" + path.join(ROOT, "cover.html"));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForLoadState("networkidle");
    await page.screenshot({ path: out });
    await browser.close();
    return;
  }
  const { browser, page } = await open();
  if (mode === "stills") {
    fs.mkdirSync(out, { recursive: true });
    for (const s of list.split(",").map(Number)) {
      await page.evaluate(t => window.render(t), s);
      await page.screenshot({ path: path.join(out, `t${s.toFixed(2)}.png`) });
    }
  } else {
    const ff = spawn("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
      "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-r", String(FPS), out], { stdio: ["pipe", "inherit", "inherit"] });
    const n = Math.round(DURATION * FPS);
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => window.render(t), i / FPS);
      const buf = await page.screenshot({ type: "png" });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
      if (i % 90 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on("close", r));
  }
  await browser.close();
})();
