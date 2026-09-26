import fs from 'node:fs';
const [,,path]=process.argv;if(!path)throw new Error('usage: node p34-verify.mjs adjudication.json');
const x=JSON.parse(fs.readFileSync(path,'utf8'));const ok=(v,m)=>{if(!v)throw new Error(m)};
ok(x.schema==='c3x-p34-adjudication-v1','schema');ok(x.scientific_stage==='C3X 0.7.0-G9.4-P34','stage');
ok(x.primary_cases===3,'case-count');ok(x.explanation_verification.unsupported_rendered_claims===0,'unsupported');
let selected=0,open=0,pos=0;
for(const z of x.certificates){
 ok(z.verification?.pass===true,'verification');const c=z.case;
 const passes=c.levels.filter(y=>y.status==='QUOTIENT_CAUSAL_CLOSURE_EXACT_DRILLDOWN_PRESERVED');
 if(c.selected_level){
  selected++;ok(passes.length===1,'passing-level-count');ok(passes[0].level===c.selected_level,'selected-first-pass');
  const q=passes[0];ok(q.minimal_remove.certified===true,'remove');ok(q.minimal_keep.certified===true,'keep');
  ok(q.drilldown.status==='PASS','drill');ok(q.drilldown.collision===false,'collision');ok(q.drilldown.large_class_hold===false,'large');
  ok(q.drilldown.remove_exact_expansion_parity===true,'remove-parity');
  ok(q.drilldown.keep_exact_expansion_parity===true,'keep-parity');
  ok(q.drilldown.query_commutation===true,'query-commutation');
  if(c.role==='OPEN_EVENT_UNIVERSE_PRIMARY')open++;if(c.role==='FINITE_CLOSURE_POSITIVE_CONTROL')pos++;
 }else{
  ok(c.status==='BOUNDED_QUOTIENT_LATTICE_DIVERGENCE','divergence-status');ok(passes.length===0,'hidden-pass');
 }
}
ok(selected===x.selected_cases,'selected-count');ok(open===x.selected_open_event_cases,'open-count');ok(pos===x.positive_control_selected,'pos-count');
console.log('P34_JS_VERIFY_PASS',x.verdict,'selected',selected,'open',open,'positive',pos);
