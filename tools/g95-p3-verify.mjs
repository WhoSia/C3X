import fs from 'node:fs';
const [,,path]=process.argv;
if(!path)throw new Error('usage: node g95-p3-verify.mjs adjudication.json');
const x=JSON.parse(fs.readFileSync(path,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error(m)};
ok(x.schema==='c3x-g95-p3-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P3','stage');
ok(x.explanation_verification.failed===0,'explanation');
ok(x.explanation_verification.unsupported_rendered_claims===0,'unsupported');
ok(x.causal_availability==='EVENT_PREFIX_ONLY','causal-availability');
ok(x.primary_selection_consulted_development_rivals===false,'development-rival-selection-leak');
for(const r of x.development_rival_census||[])ok(r.primary_eligible===false,'development-rival-primary-eligibility');
const allowed=new Set([
 'FRESH_RECONSTITUTION_SUPPORT_LIMITED_HOLD',
 'NO_TOPOLOGY_AWARE_GLOBAL_FIELD_HOLD',
 'TOPOLOGY_FIELD_SCOPE_INSUFFICIENT_HOLD',
 'TOPOLOGY_CONTEXT_CAUSAL_FIELD_HELDOUT_CERTIFIED',
 'ENGINE_CONDITIONAL_FIELDS_SUPPORTED_CROSS_ENGINE_GLUE_HOLD',
 'TOPOLOGY_FIELD_HELDOUT_FALSIFIED',
 'EXPLANATION_SERVICE_VERIFICATION_FAIL'
]);
ok(allowed.has(x.verdict),'verdict');
const sc=x.selected_global_schema_id;
if(sc!==null&&sc!==undefined)ok(['P2_BASE','TT_LOCAL','TEMPORAL_LOCAL','KEY_REUSE_TOPOLOGY','MINIMAL_HYBRID'].includes(sc),'schema-id');
for(const z of x.certificates||[]){
 const p=z.profile||{};
 for(const k of ['root_change','counterfactual_bestmove','counterfactual_score','counterfactual_wdl','counterfactual_pv'])ok(!(k in p),'profile-target-leak:'+k);
 ok(!('full_key' in (p.context||{})),'raw-key-leak');
 ok(p.causal_availability==='EVENT_PREFIX_ONLY','profile-causal-availability');
}
const hv=x.heldout_transport;
if(hv.verdict==='TOPOLOGY_CONTEXT_CAUSAL_FIELD_HELDOUT_CERTIFIED')ok(hv.global_transport_certified===true,'global-cert');
if(hv.verdict==='ENGINE_CONDITIONAL_FIELDS_SUPPORTED_CROSS_ENGINE_GLUE_HOLD'){
 ok(hv.global_transport_certified===false,'glue-global');
 for(const e of ['stockfish_19','berserk','ethereal'])ok(hv.engine_specific[e].transport_certified===true,'engine-cert:'+e);
}
console.log('G95_P3_JS_VERIFY_PASS',x.verdict,'schema',sc);
