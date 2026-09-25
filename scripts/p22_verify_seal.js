#!/usr/bin/env node
const fs=require('fs');
if(process.argv.length!==6){console.error('usage: node p22_verify_seal.js preseal.json rust.json cpp.json r.json');process.exit(2)}
const [pre,rust,cpp,ra]=process.argv.slice(2).map(p=>JSON.parse(fs.readFileSync(p,'utf8')));
function req(x,msg){if(!x)throw new Error(msg)}
req(pre.schema==='c3x-g9.4-p22-preseal-v1','P22_PRESEAL_SCHEMA');
req(pre.epistemic_reset.p21_selective_outcomes_reused===false,'P22_P21_OUTCOME_REUSE');
req(pre.epistemic_reset.p21_selected_cells_reused===false,'P22_P21_CELL_REUSE');
req(pre.epistemic_reset.p21_post_hold_28_swap_witness_cells_reused===false,'P22_P21_WITNESS_REUSE');
req(pre.design_principle.primary_gate.includes('0.50'),'P22_GATE_CHANGED');
for(const [name,x] of [['rust',rust],['cpp',cpp],['r',ra]]){req(x.gate_pass===true,`P22_${name.toUpperCase()}_GATE`);req(x.selected_count===96,`P22_${name.toUpperCase()}_COUNT`);req(Number(x.max_abs_smd)<=0.500000000001,`P22_${name.toUpperCase()}_SMD`)}
req(cpp.quota_pass===true&&ra.quota_pass===true,'P22_QUOTA_CERT');req(cpp.inanis_engagement_pass===true&&ra.inanis_engagement_pass===true,'P22_ENGAGEMENT_CERT');
const vals=[Number(rust.max_abs_smd),Number(cpp.max_abs_smd),Number(ra.max_abs_smd)];
req(Math.max(...vals)-Math.min(...vals)<=1e-9,'P22_CROSS_LANGUAGE_SMD_DISAGREEMENT');
console.log(JSON.stringify({schema:'c3x-p22-cross-language-seal-v1',authorization:'P22-SELECTIVE-INTERVENTION-AUTHORIZED',max_abs_smd:Math.max(...vals),certificates:['rust-selector','cpp-independent-cert','r-independent-audit'],selective_outcomes_consulted:false},null,2));
