import fs from 'node:fs';
const [,,p]=process.argv;if(!p)throw new Error('usage p17-verify adjudication.json');
const x=JSON.parse(fs.readFileSync(p,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error('P17_VERIFY '+m)};
ok(x.schema==='c3x-g95-p17-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P17','stage');
ok(x.world_count===216,'world-count');
ok(x.raw_tt_key_emitted===false,'raw-key');
ok(x.upper_is_diagnostic_only===true,'upper-rescue');
const valid=new Set([
'P17_HYPOTHESIS_SURVIVES_FATAL_REPLICATION_SPECIFICALLY',
'P17_HYPOTHESIS_REPLICATES_BUT_NOT_SPECIFIC',
'P17_RIVAL_FAMILY_REPLICATES_HYPOTHESIS_DEFEATED',
'P17_HYPOTHESIS_FAILS_UNDER_BALANCED_EXPOSURE',
'P17_EXPOSURE_SUPPORT_HOLD']);
ok(valid.has(x.verdict),'verdict');
if(x.status==='CLOSED_PASS')ok(x.support?.pass===true,'pass-support');
if(x.status==='HOLD')ok(x.support?.pass===false,'hold-support');
if(x.support?.pass){
 const vals=Object.values(x.support.family_exposure_counts||{});
 ok(vals.length===5&&new Set(vals).size===1,'exposure-balance');
}
const h=x.primary_hypothesis_replication||{};
if(x.verdict==='P17_HYPOTHESIS_SURVIVES_FATAL_REPLICATION_SPECIFICALLY'){
 ok(h.replicated===true,'survival-h');
 ok((x.replicated_rival_families||[]).length===0,'survival-rival');
 ok(x.h_lower_advantage_over_strongest_rival>=2,'survival-advantage');
}
if(x.verdict==='P17_RIVAL_FAMILY_REPLICATES_HYPOTHESIS_DEFEATED')
 ok((x.replicated_rival_families||[]).length>0,'rival-empty');
if(x.verdict==='P17_HYPOTHESIS_FAILS_UNDER_BALANCED_EXPOSURE')ok(h.replicated===false,'failure-h');
for(const c of x.causal_explanation_certificates||[]){
 ok(c.schema==='c3x-causal-contrast-certificate-v1','cert-schema');
 ok(c.provenance_class==='C3X_CAUSAL_CONTRAST','cert-provenance');
 ok(c.concept_label===null,'concept-null');
}
const walk=v=>{if(Array.isArray(v)){for(const z of v)walk(z);return}
 if(v&&typeof v==='object')for(const [k,z] of Object.entries(v)){
  ok(!['key','full_key','tt_key'].includes(k),'raw-key-field:'+k);walk(z)
 }};
walk(x);
console.log('P17_JS_CLAIM_FIREWALL_PASS',x.verdict,'sets',x.support?.complete_matched_sets,'Hlower',x.family_statistics?.H?.lower_minimal_full_bridges);
