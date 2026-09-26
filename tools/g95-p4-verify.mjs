#!/usr/bin/env node
import fs from "node:fs";

const [,,finalPath,deploymentPath,fieldPath,controlsPath]=process.argv;
if(!finalPath||!deploymentPath||!fieldPath||!controlsPath){
 console.error("usage: node g95-p4-verify.mjs final.json deployment.json field.json controls.json");process.exit(2);
}
const read=p=>JSON.parse(fs.readFileSync(p,"utf8"));
const f=read(finalPath),d=read(deploymentPath),field=read(fieldPath),controls=read(controlsPath);
const ok=(v,m)=>{if(!v)throw new Error(m)};
ok(f.schema==="c3x-g95-p4-adjudication-v1","final schema");
ok(f.scientific_stage==="C3X 0.7.0-G9.5-P4","stage");
ok(d.schema==="c3x-g95-p4-public-deployment-v1","deployment schema");
ok(field.schema==="c3x-field-p4-discovery-v1","field schema");
ok(controls.schema==="c3x-g95-p4-control-gate-v1"&&controls.passed===true,"positive controls");
ok(controls.fresh_support_records===0,"control support firewall");
ok(controls.controls.length===3&&controls.controls.every(x=>x.fresh_support_vote===false),"control vote");
ok(field.feature_expansion_performed===false,"feature expansion");
ok(f.explanation_verification.failed===0,"explanation verification");
ok(f.explanation_verification.unsupported_rendered_claims===0,"unsupported claims");
const allowedAst=new Set(["AUTHORITY","SAMPLING_PROVENANCE","LIMITATION"]);
for(const c of f.certificates){
 ok(c.ast.every(n=>allowedAst.has(n.type)),"AST authority surface");
}
const counts=f.public_state_counts||{};
const certified=(counts.CERTIFIED_ROOT_CHANGE||0)+(counts.CERTIFIED_NO_ROOT_CHANGE||0);
if(f.public_authority){
 ok(f.verdict==="RARE_EVENT_CAUSAL_FIELD_HELDOUT_CERTIFIED","public verdict");
 ok(d.public_global_authority===true,"deployment authority");
 ok((f.heldout.verification.contradictions||[]).length===0,"public contradictions");
 ok((f.heldout.verification.mixed_cells||[]).length===0,"public mixed cells");
}else{
 ok(d.public_global_authority===false,"deployment abstention");
 ok(certified===0,"no public certification after failed/absent transport");
 ok((counts.ABSTAIN_UNCERTIFIED_FIELD||0)===f.certificates.length,"all public abstain");
}
const selected=field.selected_global_schema;
ok((selected?.id??null)===f.selected_global_schema_id,"field identity");
console.log("G95_P4_JS_FIREWALL_PASS",f.verdict,"public",f.public_authority,"certificates",f.certificates.length);
