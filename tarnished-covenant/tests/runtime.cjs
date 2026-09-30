// Execute the actual shipped runtime offline. No credentials, backend, or real browser session.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const {webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'..');
function runtime(html=fs.readFileSync(path.join(root,'index.html'),'utf8')){
  const storage=new Map();
  let seed=123456789,uuid=0;
  const math=Object.create(Math);math.random=()=>((seed=(1664525*seed+1013904223)>>>0)/4294967296);
  class Clock extends Date { constructor(...args){super(...(args.length?args:['2026-09-30T00:00:00.000Z']))} static now(){return 1790726400000} }

  const node={appendChild(){},addEventListener(){},remove(){},querySelector(){return null},querySelectorAll(){return []},style:{},dataset:{},classList:{add(){},remove(){},toggle(){}},setAttribute(){}};
  const document={...node,querySelector(selector){return selector==='#app'?node:null},createElement(){return {...node}},head:node,body:node,documentElement:node,cookie:'',hidden:false};
  const context={console,structuredClone,URL,URLSearchParams,crypto:{...webcrypto,randomUUID:()=>`00000000-0000-4000-8000-${String(++uuid).padStart(12,'0')}`},Math:math,Date:Clock,document,navigator:{},location:{href:'https://offline.invalid/',pathname:'/',search:'',origin:'https://offline.invalid/'},history:{replaceState(){}},localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},sessionStorage:{getItem(){return null},setItem(){},removeItem(){}},queueMicrotask(){},setTimeout(){return 1},clearTimeout(){},setInterval(){return 1},clearInterval(){},requestAnimationFrame(){},MutationObserver:class{observe(){}},fetch(){throw new Error('Network access forbidden in offline tests')},addEventListener(){}};
  context.window=context;context.matchMedia=()=>({matches:false,addEventListener(){}});
  vm.createContext(context);
  const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
  let app=scripts.find(x=>x.includes('const omens = ['));
  if(!app)throw new Error('Runtime script missing');
  const boot=/^startApp\(\)\.catch\(.*$/m;
  if(!boot.test(app))throw new Error('Startup boundary changed: review offline harness');
  app=app.replace(boot,'/* offline: startup intentionally not invoked */');
  vm.runInContext(app,context,{timeout:5000});
  return {context,run(code){return vm.runInContext(code,context,{timeout:5000})},json(code){return JSON.parse(vm.runInContext('JSON.stringify('+code+')',context,{timeout:5000}))},loadBuild(){vm.runInContext(fs.readFileSync(path.join(root,'build-lab.js'),'utf8').replace('  queueMicrotask(()=>{if(run&&!tcTransitionIsLocked())renderRun();});', '  window.testBuild={saveBuild,normalizeBuild};'),context,{timeout:5000})}};
}
module.exports={runtime,root};
if(require.main===module){const app=runtime();console.log('Offline runtime loaded:',app.run('Object.keys(regions).length'),'regions');}
