import fs from 'node:fs';
const [,,p]=process.argv;if(!p)throw new Error('usage p15-verify adjudication.json');
const x=JSON.parse(fs.readFileSync(p,'utf8'));
const ok=(v,m)=>{if(!v)throw new Error('P15_VERIFY '+m)};
ok(x.schema==='c3x-g95-p15-adjudication-v1','schema');
ok(x.scientific_stage==='C3X 0.7.0-G9.5-P15','stage');
ok(x.world_count===96,'world-count');
ok(x.raw_tt_key_emitted===false,'raw-key-flag');
const valid=new Set([
 'P15_REPLICATED_CHESS_STRUCTURE_SEARCH_PREFERENCE_FULL_BRIDGE',
 'P15_REPLICATED_CHESS_STRUCTURE_SUSCEPTIBILITY_MODULATION',
 'P15_LOCAL_CHESS_STRUCTURE_SEARCH_BRIDGE_ONLY',
 'P15_BOARD_DIRECT_PREFERENCE_EFFECT_WITHOUT_SEARCH_MEDIATION',
 'P15_NO_CHESS_STRUCTURE_SEARCH_BRIDGE_UNDER_FROZEN_GRAMMAR',
 'P15_FRESH_SUPPORT_HOLD'
]);
ok(valid.has(x.verdict),'verdict');
const walk=v=>{
 if(Array.isArray(v)){for(const z of v)walk(z);return}
 if(v&&typeof v==='object'){
  for(const [k,z] of Object.entries(v)){
   ok(!['key','full_key','tt_key'].includes(k),'raw-key-field:'+k);walk(z)
  }
 }
};
walk(x);
for(const r of x.records||[]){
 ok(['FULL_BRIDGE','SUSCEPTIBILITY_MODULATION'].includes(r.kind),'record-kind');
 ok(['UPPER','LOWER'].includes(r.target_bound),'bound');
 ok(['ANCHOR_DISPREFERRED_DOMINANT','ANCHOR_PREFERRED_DOMINANT','BALANCED'].includes(r.target_relation_delta_role),'relation-role');
 if(r.kind==='FULL_BRIDGE'){
  ok(r.native_original!==r.native_target,'full-native-flip');
  ok(r.t_only_collapse_to,'full-collapse');
  ok(r.sham_reproduced===false,'full-sham');
 }
}
if(x.verdict==='P15_REPLICATED_CHESS_STRUCTURE_SEARCH_PREFERENCE_FULL_BRIDGE')
 ok((x.replicated_full_bridge_signatures||[]).length>0,'rep-full-empty');
if(x.verdict==='P15_REPLICATED_CHESS_STRUCTURE_SUSCEPTIBILITY_MODULATION')
 ok((x.replicated_susceptibility_signatures||[]).length>0,'rep-mod-empty');
if(x.status==='CLOSED_PASS')ok(x.support?.pass===true,'pass-support');
if(x.status==='HOLD')ok(x.support?.pass===false,'hold-support');
console.log('P15_JS_CLAIM_FIREWALL_PASS',x.verdict,'records',(x.records||[]).length,'active',x.support?.factorial_active_engine_worlds);
