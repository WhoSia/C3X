#!/usr/bin/env node
import fs from "node:fs";
const [,,finalPath,deploymentPath,fieldPath,verificationPath,auditPath]=process.argv;
if(!finalPath||!deploymentPath||!fieldPath||!verificationPath||!auditPath){
 console.error("usage: node g95-p6-verify.mjs final.json deployment.json field.json verification.json train-audit.json");process.exit(2);
}
const read=p=>JSON.parse(fs.readFileSync(p,"utf8"));
const f=read(finalPath),d=read(deploymentPath),field=read(fieldPath),v=read(verificationPath),audit=read(auditPath);
const ok=(x,m)=>{if(!x)throw new Error(m)};
ok(f.schema==="c3x-g95-p6-adjudication-v1","final schema");
ok(f.scientific_stage==="C3X 0.7.0-G9.5-P6","stage");
ok(d.schema==="c3x-g95-p6-public-deployment-v1","deployment schema");
ok(field.schema==="c3x-p6-selected-field-v1","field schema");
ok(v.schema==="c3x-p6-transport-verification-v1","verification schema");
ok(audit.schema==="c3x-g95-p6-train-audit-v1"&&audit.audit_pass===true,"train audit");
ok(field.post_selection_representation_mutation===false,"post-selection mutation");
ok(f.p5_selection_labels_consulted===false&&field.p5_selection_labels_consulted===false&&v.p5_selection_labels_consulted===false,"P5 label firewall");
ok(f.explanation_verification.failed===0&&f.explanation_verification.unsupported_rendered_claims===0,"explanation verification");
ok((field.selected_candidate_id??null)===(f.selected_candidate_id??null),"field identity");
const allowedAst=new Set(["AUTHORITY","RELATIONAL_REPRESENTATION","PROVENANCE","LIMITATION"]);
for(const c of f.certificates)ok(c.ast.every(n=>allowedAst.has(n.type)),"AST surface");
const counts=f.public_state_counts||{};
const certified=(counts.CERTIFIED_ROOT_CHANGE||0)+(counts.CERTIFIED_NO_ROOT_CHANGE||0);
if(f.public_authority){
 ok(f.verdict==="P6_RELATIONAL_REPRESENTATION_HELDOUT_CERTIFIED","public verdict");
 ok(d.public_global_authority===true&&v.transport_certified===true,"public authority");
 ok((v.contradictions||[]).length===0&&(v.mixed_cells||[]).length===0,"transport clean");
 ok(v.transport_targets_consulted===true&&v.target_opened_after_scope===true,"target order");
}else{
 ok(d.public_global_authority===false,"deployment abstention");
 ok(certified===0,"no public certification without transport");
 ok((counts.ABSTAIN_UNCERTIFIED_FIELD||0)===f.certificates.length,"all public abstain");
}
console.log("G95_P6_JS_FIREWALL_PASS",f.verdict,"public",f.public_authority,"certificates",f.certificates.length);
