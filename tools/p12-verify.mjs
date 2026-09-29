#!/usr/bin/env node
import fs from 'node:fs';
const [,,p]=process.argv;if(!p)throw new Error('usage p12-verify adjudication.json');
const x=JSON.parse(fs.readFileSync(p,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error('P12_VERIFY '+m)};
ok(x.schema==='c3x-g95-p12-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P12','stage');
ok(x.raw_tt_key_emitted===false,'raw-key');
ok(x.world_count===36,'world-count');
const verdicts=new Set(['P12_FRESH_SUPPORT_HOLD','P12_REPLICATED_EXACT_CUTOFF_MEDIATION','P12_EXACT_CUTOFF_MEDIATION_IDENTIFIED_REPLICATION_HOLD','P12_CUTOFF_COLOCATION_ONLY']);
ok(verdicts.has(x.verdict),'verdict');
if(x.verdict==='P12_REPLICATED_EXACT_CUTOFF_MEDIATION')ok(Array.isArray(x.replicated_mediated_transition_signatures)&&x.replicated_mediated_transition_signatures.length>0,'replicated-mediated-signature');
if(x.verdict==='P12_EXACT_CUTOFF_MEDIATION_IDENTIFIED_REPLICATION_HOLD')ok(Array.isArray(x.replicated_mediated_transition_signatures)&&x.replicated_mediated_transition_signatures.length===0&&x.support.mediated_targets>0,'mediation-replication-hold');
for(const r of x.records){
 ok(r.raw_tt_key_emitted===false,'record-key-flag');
 const s=JSON.stringify(r);
 ok(!s.includes('"key":'),'serialized-raw-key');
 ok(r.baseline_root&&r.t_only_root,'chess-root');
 if(r.root_change){
  ok(r.baseline_root.legal===true&&r.t_only_root.legal===true,'legal-root');
  ok(Number.isInteger(r.source_ply),'source-ply');
  ok(Number.isInteger(r.legal_root_move_count)&&r.legal_root_move_count>0,'legal-count');
 }
}
console.log('P12_JS_CLAIM_FIREWALL_PASS',x.verdict,'records',x.records.length,'root_change',x.support.root_change_targets);
