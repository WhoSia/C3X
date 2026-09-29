#!/usr/bin/env node
import fs from 'node:fs';
const [,,p]=process.argv;if(!p)throw new Error('usage p13-verify adjudication.json');
const x=JSON.parse(fs.readFileSync(p,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error('P13_VERIFY '+m)};
ok(x.schema==='c3x-g95-p13-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P13','stage');
ok(x.raw_tt_key_emitted===false,'raw-key');
ok(x.world_count===48,'world-count');
const verdicts=new Set(['P13_REPLICATED_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY','P13_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY_LOCAL_ONLY','P13_ROOT_CANDIDATE_COMPETITION_REDIRECTION_WITHOUT_PAIRWISE_BOUNDARY_REPLICATION','P13_NO_ROOT_PREFERENCE_BOUNDARY_EFFECT_UNDER_FROZEN_EXACT_EVENT_INTERVENTION','P13_FRESH_SUPPORT_HOLD']);
ok(verdicts.has(x.verdict),'verdict');
if(x.verdict==='P13_REPLICATED_PAIRWISE_PREFERENCE_BOUNDARY_CAUSALITY')ok(x.replicated_direct_pair_flip_signatures?.length>0,'replication');
ok((x.support.pass&&x.status==='CLOSED_PASS')||(!x.support.pass&&x.status==='HOLD'),'status');
const forbidden=new Set(['key','full_key','tt_key']);
const walk=v=>{if(Array.isArray(v)){for(const z of v)walk(z)}else if(v&&typeof v==='object'){for(const [k,z] of Object.entries(v)){ok(!forbidden.has(k),'raw-key-field');walk(z)}}};
walk(x);
for(const r of x.records){
 ok(r.raw_tt_key_emitted===false,'record-key');
 ok(r.baseline_root?.legal===true&&r.t_only_root?.legal===true,'legal-root');
 if(r.effect_category==='DIRECT_PAIR_FLIP'){
  ok(r.preference_boundary_crossed===true,'flip-flag');
  ok(r.t_only_root.uci===r.isolated_pair.rival.uci,'flip-rival');
 }
}
console.log('P13_JS_CLAIM_FIREWALL_PASS',x.verdict,'records',x.records.length,'qualified',x.support.qualified_worlds);
