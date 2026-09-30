#!/usr/bin/env node
const fs=require("fs");
const x=JSON.parse(fs.readFileSync(process.argv[2],"utf8"));
if(x.schema!=="c3x-g95-p18-adjudication-v1") throw Error("schema");
const allowed=new Set(["P18_HYPOTHESIS_SURVIVES_SUPPORT_REALIZED_FATAL_REPLICATION","P18_HYPOTHESIS_REPLICATES_BUT_NOT_SPECIFIC","P18_RIVAL_REPLICATES_HYPOTHESIS_DEFEATED","P18_HYPOTHESIS_FAILS_WITH_ADEQUATE_SUPPORT","P18_CONFIRMATION_SUPPORT_HOLD","P18_DEVELOPMENT_ECOLOGY_HOLD"]);
if(!allowed.has(x.verdict)) throw Error("verdict");
if(x.upper_is_diagnostic_only!==true) throw Error("upper");
if(x.raw_tt_key_emitted!==false) throw Error("raw");
if(x.verdict==="P18_HYPOTHESIS_SURVIVES_SUPPORT_REALIZED_FATAL_REPLICATION"){
 if(!x.confirmation_support.pass) throw Error("survival_without_support");
 if(!x.primary_hypothesis_replication?.replicated) throw Error("survival_without_replication");
 if((x.replicated_rival_families||[]).length) throw Error("rival_replication");
 if(x.h_lower_advantage_over_strongest_rival<2) throw Error("specificity");
}
for(const c of x.causal_explanation_certificates||[]){
 if(c.provenance_class!=="C3X_CAUSAL_CONTRAST") throw Error("provenance");
 if(c.concept_label!==null) throw Error("concept");
}
console.log("P18_JS_CLAIM_FIREWALL_PASS",x.verdict,"sets",x.confirmation_support.complete_matched_sets,"certs",(x.causal_explanation_certificates||[]).length);
