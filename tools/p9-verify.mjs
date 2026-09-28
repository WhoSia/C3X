#!/usr/bin/env node
import fs from "node:fs";
const [,,mapPath,goPath]=process.argv;
if(!mapPath||!goPath){console.error("usage: node p9-verify.mjs map.json go-parity.json");process.exit(2);}
const m=JSON.parse(fs.readFileSync(mapPath,"utf8"));
const g=JSON.parse(fs.readFileSync(goPath,"utf8"));
const ok=(x,msg)=>{if(!x)throw new Error(msg)};
ok(m.schema==="c3x-g95-p9-map-v1","map schema");
ok(m.scientific_stage==="C3X 0.7.0-G9.5-P9","stage");
ok(g.schema==="c3x-g95-p9-go-map-parity-v1"&&g.pass===true,"Go parity");
ok(m.winner_selected===false,"no winner selection");
ok(m.post_target_threshold_refit===false,"no post-target refit");
ok(m.p8_target_labels_consulted===false,"P8 firewall");
ok(!Object.prototype.hasOwnProperty.call(m,"best_phase"),"best phase forbidden");
const declared=new Set(m.operational_hotspot_phases||[]);
for(const p of m.phase_map||[])ok(Boolean(p.operational_hotspot)===declared.has(p.phase),"hotspot list parity");
if(m.status==="SUPPORT_HOLD"){
 ok(declared.size===0,"no hotspot authority on support hold");
 ok((m.regression_suite||[]).length===0,"no regression bank on support hold");
}else{
 ok(m.status==="CARTOGRAPHY_COMPLETE","status");
}
console.log("P9_JS_CLAIM_FIREWALL_PASS",m.status,"hotspots",declared.size);
