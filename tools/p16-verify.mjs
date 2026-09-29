import fs from 'node:fs';
const [,,p]=process.argv;if(!p)throw new Error('usage p16-verify adjudication.json');
const x=JSON.parse(fs.readFileSync(p,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error('P16_VERIFY '+m)};
ok(x.schema==='c3x-g95-p16-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P16','stage');
ok(x.world_count===108,'world-count');
ok(x.raw_tt_key_emitted===false,'raw-key');
const valid=new Set([
'P16_REPLICATED_MINIMAL_STRUCTURAL_EQUIVALENCE_FULL_BRIDGE',
'P16_REPLICATED_FULL_PREFERENCE_MEDIATION_NO_STABLE_MINIMAL_EQUIVALENCE',
'P16_LOCAL_MINIMAL_FULL_BRIDGE_ONLY',
'P16_REPLICATED_SUSCEPTIBILITY_ONLY',
'P16_NO_FULL_BRIDGE_UNDER_FROZEN_MINIMIZATION_FAMILY',
'P16_FRESH_SUPPORT_HOLD']);
ok(valid.has(x.verdict),'verdict');
if(x.status==='CLOSED_PASS')ok(x.support?.pass===true,'pass-support');
if(x.status==='HOLD')ok(x.support?.pass===false,'hold-support');
for(const c of x.causal_explanation_certificates||[]){
 ok(c.schema==='c3x-causal-contrast-certificate-v1','cert-schema');
 ok(c.provenance_class==='C3X_CAUSAL_CONTRAST','cert-provenance');
 ok(c.concept_label===null,'concept-null');
 ok(c.subset_reproduced===false,'minimal-subset');
 ok(c.sham_reproduced===false,'minimal-sham');
}
if(x.verdict==='P16_REPLICATED_MINIMAL_STRUCTURAL_EQUIVALENCE_FULL_BRIDGE')
 ok((x.replicated_exact_structural_signatures||[]).length>0,'exact-empty');
if(x.verdict==='P16_REPLICATED_FULL_PREFERENCE_MEDIATION_NO_STABLE_MINIMAL_EQUIVALENCE'){
 ok((x.replicated_exact_structural_signatures||[]).length===0,'unexpected-exact');
 ok((x.replicated_coarse_full_bridge_signatures||[]).length>0,'coarse-empty');
}
const walk=v=>{
 if(Array.isArray(v)){for(const z of v)walk(z);return}
 if(v&&typeof v==='object')for(const [k,z] of Object.entries(v)){
  ok(!['key','full_key','tt_key'].includes(k),'raw-key-field:'+k);walk(z)
 }
};
walk(x);
console.log('P16_JS_CLAIM_FIREWALL_PASS',x.verdict,'minimal',x.minimal_full_bridge_records,'certificates',(x.causal_explanation_certificates||[]).length);
