import fs from 'node:fs';

const [,,path]=process.argv;
if(!path)throw new Error('usage: node g95-p1-verify.mjs adjudication.json');
const x=JSON.parse(fs.readFileSync(path,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error(m)};

ok(x.schema==='c3x-g95-p1-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P1','stage');
ok(x.explanation_verification.unsupported_rendered_claims===0,'unsupported');
ok(x.explanation_verification.failed===0,'explanation-verification');
const allowed=new Set([
 'DISCOVERY_FIBER_CONSTITUTION_HOLD',
 'DISCOVERY_FIBER_HOLDOUT_FALSIFIED',
 'WITNESS_PRESERVING_HOLDOUT_PASS_FRESH_TRANSPORT_COLLISION_HOLD',
 'WITNESS_PRESERVING_LOCAL_FIBER_CROSS_CONTEXT_HOLD',
 'WITNESS_PRESERVING_CAUSAL_FIBER_TRANSPORT_CERTIFIED',
 'EXPLANATION_OR_FIBER_VERIFICATION_FAIL'
]);
ok(allowed.has(x.verdict),'verdict');

for(const z of x.certificates){
 const c=z.case;
 for(const r of c.records||[]){
  const s=JSON.stringify(r.diagnostic);
  ok(!/bestmove|score|wdl|\bpv\b|root_change|fen|address_id|full_key|engine/i.test(s),'diagnostic-target-leak');
  ok(Object.keys(r.fibers).join(',')==='F0,F1,F2,F3','fiber-levels');
 }
 for(const v of Object.values(c.fiber_verification||{})){
  ok(v.target_fields_consulted===false,'rust-target-leak');
  ok((v.mismatches||[]).length===0,'rust-mismatch');
 }
}

if(x.selected_level===null){
 ok(x.verdict==='DISCOVERY_FIBER_CONSTITUTION_HOLD','null-level-verdict');
}else{
 ok(['F0','F1','F2','F3'].includes(x.selected_level),'selected-level');
 const h=x.binding_holdout;
 ok(h!==null && h!==undefined,'holdout-missing');
 if(!h.pass){
  ok(x.verdict==='DISCOVERY_FIBER_HOLDOUT_FALSIFIED','holdout-fail-verdict');
 }else{
  const local=x.transport.fresh_within_world_collision_count;
  const global=x.transport.fresh_global;
  ok(global && typeof global.collision_count==='number','fresh-global');
  if(local>0)ok(x.verdict==='WITNESS_PRESERVING_HOLDOUT_PASS_FRESH_TRANSPORT_COLLISION_HOLD','fresh-local-verdict');
  else if(global.collision_count>0)ok(x.verdict==='WITNESS_PRESERVING_LOCAL_FIBER_CROSS_CONTEXT_HOLD','cross-context-verdict');
  else ok(x.verdict==='WITNESS_PRESERVING_CAUSAL_FIBER_TRANSPORT_CERTIFIED','certified-verdict');
 }
}
console.log('G95_P1_JS_VERIFY_PASS',x.verdict,'selected',x.selected_level);
