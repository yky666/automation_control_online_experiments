import fs from 'node:fs';
import katex from 'katex';
const catalog=JSON.parse(fs.readFileSync(new URL('../docs/catalog-qa.json',import.meta.url),'utf8'));
let count=0;
for(const lab of catalog) for(const s of lab.sections) for(const tex of s.formulas){katex.renderToString(tex,{throwOnError:true,displayMode:true});count++;}
console.log(`PASS: ${count} formulas render with KaTeX.`);
