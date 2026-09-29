#!/usr/bin/env node
import fs from 'node:fs';
const [,,p]=process.argv;if(!p)throw new Error('usage p14-verify adjudication.json');
const x=JSON.parse(fs.readFileSync(p,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error('P14_VERIFY '+m)};
ok(x.schema==='c3x-g95-p14-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P14','stage');
ok(x.raw_tt_key_emitted===false,'raw-key');
ok(x.world_count===72,'world-count');
const verdicts=new Set(['P14_REPLICATED_RECIPROCAL_CROSS_ENGINE_PAIR_GEOMETRY','P14_REPLICATED_ORIENTATION_FREE_PAIR_REVERSAL_TRANSPORT','P14_LOCAL_MULTIENGINE_UNORDERED_PAIR_TRANSPORT_ONLY','P14_LOCAL_UNORDERED_PAIR_EDGE_CAUSALITY_ONLY','P14_NO_PAIR_EDGE_REVERSAL_UNDER_FROZEN_EXACT_EVENT_INTERVENTION','P14_FRESH_SUPPORT_HOLD']);
ok(verdicts.has(x.verdict),'verdict');
if(x.verdict==='P14_REPLICATED_RECIPROCAL_CROSS_ENGINE_PAIR_GEOMETRY')ok(x.replicated_reciprocal_signatures?.length>0,'reciprocal-replication');
if(x.verdict==='P14_REPLICATED_ORIENTATION_FREE_PAIR_REVERSAL_TRANSPORT')ok(x.replicated_orientation_free_reversal_signatures?.length>0,'event-replication');
ok((x.support.pass&&x.status==='CLOSED_PASS')||(!x.support.pass&&x.status==='HOLD'),'status');
const forbidden=new Set(['key','full_key','tt_key']);
const walk=v=>{if(Array.isArray(v)){for(const z of v)walk(z)}else if(v&&typeof v==='object'){for(const [k,z] of Object.entries(v)){ok(!forbidden.has(k),'raw-key-field');walk(z)}}};
walk(x);
for(const r of x.records){
 ok(r.raw_tt_key_emitted===false,'record-key');
 ok(['BASELINE_PREFERRED','BASELINE_DISPREFERRED'].includes(r.target_relation),'target-relation');
 ok(r.pair?.A?.legal===true&&r.pair?.B?.legal===true&&r.baseline_preferred?.legal===true&&r.t_only_root?.legal===true,'legal-moves');
 const lexical=[r.pair.A.uci,r.pair.B.uci].sort();
 ok(lexical[0]===r.pair.A.uci&&lexical[1]===r.pair.B.uci,'canonical-pair');
 if(r.effect_category==='EDGE_REVERSAL'){
  ok(r.edge_reversed===true,'reversal-flag');
  const other=r.baseline_preferred.uci===r.pair.A.uci?r.pair.B.uci:r.pair.A.uci;
  ok(r.t_only_root.uci===other,'reversal-other-member');
 }
}
console.log('P14_JS_CLAIM_FIREWALL_PASS',x.verdict,'records',x.records.length,'pairs',x.support.admitted_pair_positions,'active',x.support.active_engine_worlds);
