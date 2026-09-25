#!/usr/bin/env node
import fs from 'node:fs';

const [prePath,outPath,reportPath]=process.argv.slice(2);
if(!prePath||!outPath||!reportPath){console.error('usage: node tools/p25-verify.mjs <precommit.json> <adjudication.json> <report.md>');process.exit(2)}
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const pre=read(prePath),out=read(outPath);
const assert=(x,m)=>{if(!x)throw new Error(`P25_VERIFY ${m}`)};
const stable=x=>JSON.stringify(x);
const targets=['stockfish_19','berserk','ethereal'];
assert(pre.schema==='c3x-p25-precommit-v1','precommit schema');
assert(out.schema==='c3x-p25-adjudication-v1','adjudication schema');
assert(pre.scientific_stage==='C3X 0.7.0-G9.4-P25'&&out.scientific_stage===pre.scientific_stage,'stage');
assert(pre.selective_outcomes_consulted===false,'outcome-blind precommit');
assert(stable(pre.budgets)==='[40000,80000,160000,300000]','budget constitution');
assert(pre.canonical_atlas_nodes===80000&&pre.selective_intervention_nodes===300000,'canonical budgets');
assert(Object.keys(pre.budget_stability).length===6,'all six budget pairs');

const k8=out.court.K8;
assert(k8.states.length===8,'K8 state count');
const common=[];
for(const s of k8.states){
  const sig=targets.map(t=>stable([k8.fingerprints[s][t].HEAVY_HEAVY,k8.fingerprints[s][t].MINOR_MINOR]));
  if(new Set(sig).size===1)common.push(s);
}
assert(stable(common)===stable(out.architecture_free_k8_states),'architecture-free states recompute');
const nonconstant=targets.every(t=>k8.distinct_response_laws_by_engine[t]>1);
assert(nonconstant===out.architecture_indexed_law_nonconstant_each_engine,'nonconstant law recompute');
const replication=common.length===0&&nonconstant;
assert(replication===out.architecture_index_replication,'replication branch recompute');

const signatures=out.full_k8_law_signatures;
const subsets=pre.descriptor_authority.candidate_subsets_in_test_order;
const desc=pre.engine_descriptors;
let minimal=null;const mins=[];
for(const subset of subsets){
  const groups=new Map();
  for(const e of targets){
    const key=stable(subset.map(c=>desc[e][c]));
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(e);
  }
  let ok=true;
  for(const members of groups.values()){
    if(new Set(members.map(e=>stable(signatures[e]))).size>1){ok=false;break}
  }
  if(ok){
    if(minimal===null)minimal=subset.length;
    if(subset.length===minimal)mins.push(stable(subset));
  }
}
assert(minimal===out.descriptor_compression.minimal_descriptor_cardinality,'minimal descriptor cardinality');
const reported=new Set(out.descriptor_compression.minimal_sufficient_subsets.map(x=>stable(x.coordinates)));
assert(mins.every(x=>reported.has(x))&&reported.size===mins.length,'minimal descriptor subsets');
assert(out.descriptor_compression.one_coordinate_identified===(minimal===1),'one-coordinate branch');

const expected=replication&&minimal!==null
  ?'FRESH_ARCHITECTURE_INDEX_REPLICATED__BUDGET_ATLAS_MEASURED__FROZEN_DESCRIPTOR_MORPHISM_IDENTIFIED'
  :replication
    ?'FRESH_ARCHITECTURE_INDEX_REPLICATED__BUDGET_ATLAS_MEASURED__DESCRIPTOR_IDENTIFICATION_UNDERDETERMINED'
    :'P25_REPLICATION_NOT_CONFIRMED__DESCRIPTOR_COURT_REMAINS_DESCRIPTIVE';
assert(out.verdict===expected,'verdict branch');

const lines=[
  '# C3X G9.4-P25 independent semantic verification',
  '',
  `- verdict: **${out.verdict}**`,
  `- fresh architecture-index replication: **${replication}**`,
  `- architecture-free K8 states: **${common.length}/8**`,
  `- nonconstant law in every engine: **${nonconstant}**`,
  `- frozen descriptor minimal cardinality: **${minimal===null?'none':minimal}**`,
  `- one-coordinate descriptive sufficiency: **${minimal===1}**`,
  `- budget-pair stability readouts: **${Object.keys(pre.budget_stability).length}/6**`,
  '',
  'PASS: JavaScript independently recomputed the scientific branch logic from sealed artifacts. It does not pretend to reproduce Python float-JSON byte hashes.'
];
fs.writeFileSync(reportPath,lines.join('\n')+'\n');
console.log('P25_VERIFY_PASS',expected);
