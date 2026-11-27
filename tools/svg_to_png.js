// An SVG -> PNG at 2x in the light colour scheme (for print), with the Chromium + Playwright here.
//     node tools/svg_to_png.js <in.svg> <out.png>
// Used for the SQL Generator example's Help diagram:
//     node tools/svg_to_png.js "src/SQLGeneratorExample/SQL Generator Object Model.svg" "src/SQLGeneratorExample/SQL Generator Diagram.png"
// (run it again after tools/make_sql_generator_svg.py changes the SVG)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [svgPath, pngPath] = process.argv.slice(2);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const m = svg.match(/width="(\d+)"\s+height="(\d+)"/);
  const width = m ? +m[1] : 1000, height = m ? +m[2] : 1000;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2, colorScheme: 'light' });
  await page.goto('file://' + path.resolve(svgPath));
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width, height } });
  await browser.close();
})();
