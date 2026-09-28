#!/usr/bin/env node
import fs from "node:fs";
const [,,finalPath,deploymentPath,trainPath,fieldPath,verificationPath]=process.argv;
if(!verificationPath){console.error("usage: node g95-p7-verify.mjs final deployment train field verification");process.exit(2)}
const read=p=>JSON.parse(fs.readFileSync(p,"utf8"));const f=read(finalPath),d=read(deploymentPath),tr=read(trainPath),field=read(fieldPath),v=read(verificationPath);
const ok=(x,m)=>{if(!x)throw new Error(m)};
ok(f.schema==="c3x-g95-p7-adjudication-v1","final schema");ok(d.schema==="c3x-g95-p7-public-deployment-v1","deployment schema");
ok(tr.schema==="c3x-p7-train-field-v1","train schema");ok(field.schema==="c3x-p7-selected-field-v1","field schema");
ok(v.schema==="c3x-p7-transport-verification-v1","verification schema");
ok(f.p6_target_labels_consulted===false&&f.p6_near_miss_diagnostics_consulted===false,"P6 firewall");
ok(tr.post_target_graph_mutation===false,"graph mutation");ok(field.post_selection_refit===false,"selection refit");
ok(f.explanation_verification.failed===0&&f.explanation_verification.unsupported_rendered_claims===0,"explanation verification");
const allowed=new Set(["AUTHORITY","CHESS_SEARCH_STATE","CHESS_POSITION","CHESS_PHENOTYPE","LIMITATION"]);
for(const c of f.certificates)ok(c.ast.every(n=>allowed.has(n.type)),"AST surface");
const counts=f.public_state_counts||{};const cert=(counts.CERTIFIED_ROOT_CHANGE||0)+(counts.CERTIFIED_NO_ROOT_CHANGE||0);
if(f.public_authority){
 ok(f.verdict==="P7_PREFIX_GRAPH_CAUSAL_STATE_HELDOUT_CERTIFIED","public verdict");
 ok(v.transport_certified===true&&v.transport_targets_consulted===true&&v.target_opened_after_scope===true,"transport authority");
 ok((v.contradictions||[]).length===0&&(v.mixed_states||[]).length===0,"transport clean");
}else{
 ok(d.public_global_authority===false,"deployment authority");ok(cert===0,"no public cert without heldout authority");
 ok((counts.ABSTAIN_UNCERTIFIED_FIELD||0)===f.certificates.length,"all public abstain");
}
console.log("G95_P7_JS_AUTHORITY_PASS",f.verdict,"public",f.public_authority,"certificates",f.certificates.length);
