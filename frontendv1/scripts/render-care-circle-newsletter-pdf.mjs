import fs from "fs/promises";
import path from "path";
import { chromium } from "playwright";

async function main() {
  const inputPath = process.argv[2];
  const outputPath = process.argv[3];

  if (!inputPath || !outputPath) {
    throw new Error("Usage: node frontendv1/scripts/render-care-circle-newsletter-pdf.mjs <input-html> <output-pdf>");
  }

  const absoluteInput = path.resolve(inputPath);
  const absoluteOutput = path.resolve(outputPath);
  const html = await fs.readFile(absoluteInput, "utf-8");
  await fs.mkdir(path.dirname(absoluteOutput), { recursive: true });

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "networkidle" });
    await page.pdf({
      path: absoluteOutput,
      format: "Letter",
      margin: {
        top: "0.5in",
        right: "0.5in",
        bottom: "0.5in",
        left: "0.5in",
      },
      printBackground: true,
    });
  } finally {
    await browser.close();
  }

  console.log(absoluteOutput);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
