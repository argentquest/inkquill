const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

async function main() {
  const [, , htmlArg, pdfArg] = process.argv;
  if (!htmlArg || !pdfArg) {
    throw new Error("Usage: node render_newsletter_pdf.js <htmlPath> <pdfPath>");
  }

  const htmlPath = path.resolve(htmlArg);
  const pdfPath = path.resolve(pdfArg);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1280, height: 1810 },
    deviceScaleFactor: 1,
  });

  await page.goto(pathToFileURL(htmlPath).href, {
    waitUntil: "load",
    timeout: 120000,
  });

  await page.emulateMedia({ media: "print" });

  await page.waitForFunction(() => Array.from(document.images).every((img) => img.complete), null, {
    timeout: 120000,
  });

  await page.pdf({
    path: pdfPath,
    format: "Letter",
    printBackground: true,
    margin: {
      top: "0.35in",
      right: "0.35in",
      bottom: "0.35in",
      left: "0.35in",
    },
    preferCSSPageSize: true,
  });

  await browser.close();
}

main().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
