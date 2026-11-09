// node tools/svg_to_pdf.js out.pdf page1.svg page2.svg ...
// Renders each SVG (sized in mm) as one A4 page of a single PDF.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [out, ...svgs] = process.argv.slice(2);
  const html = '<!doctype html><html><head><style>@page{size:A4;margin:0}body{margin:0}' +
    '.p{width:210mm;height:297mm;page-break-after:always;overflow:hidden}</style></head><body>' +
    svgs.map(f => '<div class="p">' + fs.readFileSync(f, 'utf8').replace(/<\?xml[^>]*>/, '') + '</div>').join('') +
    '</body></html>';
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.setContent(html);
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
