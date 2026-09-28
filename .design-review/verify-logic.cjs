const fs = require('node:fs');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {parse} = require('C:/Users/daniel jay bernadas/AppData/Local/npm-cache/_npx/249ca9fcd30c476a/node_modules/@babel/parser/lib/index.js');
const omitted = new Set(['start','end','loc','extra','comments','leadingComments','trailingComments','innerComments']);
function normalize(value) {
  if(!value || typeof value !== 'object') return value;
  if(Array.isArray(value)) return value.map(normalize);
  if(value.type === 'JSXElement' || value.type === 'JSXFragment') return {type:'Presentation'};
  return Object.fromEntries(Object.entries(value).filter(([key])=>!omitted.has(key)).map(([key,val])=>[key,normalize(val)]));
}
function handlers(node, list=[]) {
  if(!node || typeof node !== 'object') return list;
  if(node.type==='JSXAttribute' && /^on[A-Z]/.test(node.name.name)) list.push(normalize(node));
  for(const [key,val] of Object.entries(node)) if(!omitted.has(key)) {
    if(Array.isArray(val)) val.forEach(child=>handlers(child,list));
    else if(val && typeof val==='object') handlers(val,list);
  }
  return list;
}
for(const name of ['Storefront','AuthPage','AdminDashboard','UI']) {
  const before = parse(fs.readFileSync(`.design-review/before/${name}.jsx`,'utf8'),{sourceType:'module',plugins:['jsx']});
  const after = parse(fs.readFileSync(`src/components/${name}.jsx`,'utf8'),{sourceType:'module',plugins:['jsx']});
  assert.deepEqual(normalize(after),normalize(before),`${name}: application logic changed`);
  assert.deepEqual(handlers(after),handlers(before),`${name}: event handlers changed`);
  console.log(`${name}: identical non-markup code and all event handlers`);
}
for(const {Path,Hash} of JSON.parse(fs.readFileSync('.design-review/unchanged-files.json','utf8').replace(/^\uFEFF/,''))) {
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(Path)).digest('hex').toUpperCase(),Hash);
  console.log(`${Path.split('\\').pop()}: unchanged`);
}
