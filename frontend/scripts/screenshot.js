#!/usr/bin/env node
/**
 * Screenshot utility for Scivly frontend
 * Usage: node scripts/screenshot.js [url] [output]
 * Default: node scripts/screenshot.js http://localhost:3000 ./screenshots/home.png
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function takeScreenshot(url, outputPath) {
  const targetUrl = url || 'http://localhost:3000';
  const output = outputPath || './screenshots/home.png';

  // Ensure screenshots directory exists
  const dir = path.dirname(output);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  console.log(`📸 Taking screenshot of ${targetUrl}...`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });

  const page = await context.newPage();

  try {
    await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 30000 });

    // Wait for fonts to load
    await page.waitForTimeout(1000);

    await page.screenshot({
      path: output,
      fullPage: true,
    });

    console.log(`✅ Screenshot saved to ${output}`);
  } catch (error) {
    console.error(`❌ Error taking screenshot: ${error.message}`);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Capture multiple pages
async function captureAll() {
  const baseUrl = process.env.BASE_URL || 'http://localhost:3000';
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputDir = `./screenshots/${timestamp}`;

  const pages = [
    { path: '/', name: 'home' },
    { path: '/docs', name: 'docs' },
    { path: '/admin', name: 'admin' },
  ];

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });

  fs.mkdirSync(outputDir, { recursive: true });

  for (const { path: pagePath, name } of pages) {
    const page = await context.newPage();
    const url = `${baseUrl}${pagePath}`;
    const output = `${outputDir}/${name}.png`;

    try {
      console.log(`📸 Capturing ${name}...`);
      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(1000);
      await page.screenshot({ path: output, fullPage: true });
      console.log(`  ✅ ${output}`);
    } catch (error) {
      console.error(`  ❌ Failed: ${error.message}`);
    } finally {
      await page.close();
    }
  }

  await browser.close();
  console.log(`\n🎉 All screenshots saved to ${outputDir}/`);
}

// CLI
const args = process.argv.slice(2);
if (args[0] === 'all') {
  captureAll();
} else {
  takeScreenshot(args[0], args[1]);
}
