#!/usr/bin/env node
import fs from "node:fs";
const [,,anatomyPath,goPath,regPath]=process.argv;
if(!anatomyPath||!goPath||!regPath){console.error("usage: node p10-verify.mjs anatomy go regression");process.exit(2)}
const a=JSON.parse(fs.readFileSync(anatomyPath,"utf8"));
const g=JSON.parse(fs.readFileSync(goPath,"utf8"));
const r=JSON.parse(fs.readFileSync(regPath,"utf8"));
const ok=(x,m)=>{if(!x)throw new Error(m)};
ok(a.schema==="c3x-g95-p10-anatomy-v1","anatomy schema");
ok(a.scientific_stage==="C3X 0.7.0-G9.5-P10","stage");
ok(g.schema==="c3x-g95-p10-go-anatomy-parity-v1"&&g.pass===true,"Go parity");
ok(a.p9_target_labels_consulted===false,"P9 fresh-label firewall");
ok(a.p9_regression_witnesses_confirmatory_vote===false,"P9 regression vote");
ok(a.a1_may_rescue_a0===false&&a.post_target_archetype_refit===false,"no anatomy rescue/refit");
ok(a.raw_tt_key_emitted===false,"raw key firewall");
ok(r.schema==="c3x-g95-p10-p9-seed-replay-v1","regression schema");
ok(r.authority==="ENGINEERING_REPRODUCTION_ONLY"&&r.fresh_confirmatory_vote===false,"regression authority");
if(r.pass!==true)throw new Error("baseline regression harness not reproducible");
for(const z of a.replicated_a0_archetypes||[]){
 ok(z.root_change>=4,"A0 root count");ok((z.positive_engines||[]).length>=2,"A0 engine breadth");
 ok((z.positive_positions||[]).length>=2,"A0 position breadth");ok((z.positive_sources||[]).length>=2,"A0 source breadth");
}
console.log("P10_JS_CLAIM_FIREWALL_PASS",a.status,"replicated_a0",(a.replicated_a0_archetypes||[]).length,"regression_cases",r.case_count);
