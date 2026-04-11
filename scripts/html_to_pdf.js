/**
 * Converts an HTML file to PDF using Playwright Chromium.
 * Usage: node html_to_pdf.js <input.html> <output.pdf>
 */
const { chromium } = require('playwright');
const path = require('path');

async function main() {
  const [, , htmlFile, pdfFile] = process.argv;
  if (!htmlFile || !pdfFile) {
    console.error('Usage: node html_to_pdf.js <input.html> <output.pdf>');
    process.exit(1);
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  const fileUrl = 'file:///' + path.resolve(htmlFile).replace(/\\/g, '/');
  await page.goto(fileUrl, { waitUntil: 'networkidle' });

  // Wait for any lazy-rendered content
  await page.waitForTimeout(500);

  await page.pdf({
    path: pdfFile,
    format: 'A4',
    printBackground: true,
    margin: { top: '0.4in', bottom: '0.4in', left: '0.4in', right: '0.4in' },
  });

  await browser.close();
  console.log('PDF written to', pdfFile);
}

main().catch(err => { console.error(err); process.exit(1); });
