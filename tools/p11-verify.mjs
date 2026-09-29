#!/usr/bin/env node
const fs=require('fs');
const [,,adjPath,regPath]=process.argv;
if(!adjPath||!regPath)throw new Error('usage p11-verify adjudication regression');
const a=JSON.parse(fs.readFileSync(adjPath,'utf8')),r=JSON.parse(fs.readFileSync(regPath,'utf8'));
const ok=(x,m)=>{if(!x)throw new Error('P11_VERIFY '+m)};
ok(a.schema==='c3x-g95-p11-adjudication-v1','schema');
ok(a.scientific_stage==='C3X 0.7.0-G9.5-P11','stage');
ok(a.fresh_confirmatory_vote===false,'fresh-vote');
ok(a.raw_tt_key_emitted===false,'raw-key');
ok(a.support.targets===17&&a.support.exact_parent_replays===17,'parent-replay');
ok(a.support.valid_engines.length>=2&&a.support.valid_bound_variants.length>=2,'spread');
ok(r.schema==='c3x-g95-p11-patch-regression-v1'&&r.case_count===7,'reg-schema');
ok(r.none_mode_pass===true&&r.fresh_confirmatory_vote===false,'none-mode');
const none=r.rows.filter(x=>x.patch_mode==='NONE');
ok(none.length===7&&none.every(x=>x.classification==='SURVIVES_EXACTLY'),'none-survival');
const classes=new Set(['SURVIVES_EXACTLY','EFFECT_DISAPPEARS','EFFECT_REDIRECTS','EVENT_ADDRESS_DRIFTS','BASELINE_DRIFT','CONTROL_BREAKS','NONCOMPARABLE']);
ok(r.rows.every(x=>classes.has(x.classification)),'classification');
for(const c of a.cases){
  ok(c.raw_tt_key_emitted===false,'case-key');
  ok(!JSON.stringify(c).includes('"key":'),'serialized-key');
  ok(['OBSERVED_PATH_DIVERGENCE','MEDIATOR_CLASS_CAUSAL_ALIGNMENT','MEDIATOR_CLASS_INTERACTION_REDIRECT','NO_POST_TARGET_MEDIATOR_CANDIDATE'].includes(c.mediation_status),'med-status');
}
console.log('P11_JS_CLAIM_FIREWALL_PASS',a.verdict,'targets',a.support.targets,'patch_rows',r.rows.length);
