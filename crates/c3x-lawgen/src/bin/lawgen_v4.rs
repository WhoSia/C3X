use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

fn canon(v:&Value)->Vec<u8>{
 let mut x=v.clone();
 fn sort(v:&mut Value){
  match v{
   Value::Object(m)=>{
    let old=std::mem::take(m);
    let mut kv:Vec<_>=old.into_iter().collect();
    kv.sort_by(|a,b|a.0.cmp(&b.0));
    for (k,mut z) in kv { sort(&mut z); m.insert(k,z); }
   },
   Value::Array(a)=>for z in a { sort(z); },
   _=>{}
  }
 }
 sort(&mut x);
 serde_json::to_vec(&x).unwrap()
}
fn sha(v:&Value)->String{
 let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())
}
fn main(){
 let a:Vec<String>=env::args().collect();
 assert_eq!(a.len(),3);
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v4");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P28");
 assert_eq!(s["scope"]["dose_decoy_counts"],json!([0,1,3,7]));
 assert_eq!(s["scope"]["anchor_dose"],3);
 assert_eq!(s["scope"]["selected_cells"],128);
 assert_eq!(s["conditional_morphism"]["held_out_architecture"],"ethereal");
 let ss=sha(&s);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v4",
  "scientific_stage":s["scientific_stage"],
  "title":s["title"],
  "spec_sha256":ss,
  "parent_authority":s["parent_authority"],
  "scope":s["scope"],
  "mediator_contract":s["mediator_contract"],
  "dose_response":s["dose_response"],
  "conditional_morphism":s["conditional_morphism"],
  "ethereal_null_localization":s["ethereal_null_localization"],
  "collision_graph_witness":s["collision_graph_witness"],
  "portability_contract":s["portability_contract"],
  "lawgen_v4":s["lawgen_v4"],
  "literature_constraints":s["literature_constraints"],
  "prospective_claims":s["prospective_claims"],
  "claim_ceiling":s["claim_ceiling"],
  "selective_outcomes_consulted":false
 });
 let cs=sha(&c);
 let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("mediation-contract.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-p28-mediation-contract-v1",
  "scientific_stage":"C3X 0.7.0-G9.4-P28",
  "constitution_sha256":cs,
  "dose_ladder":[0,1,3,7],
  "law_anchor_dose":3,
  "mediator_signature":"exact OFF->ON hit-rate sign at each dose",
  "heldout_order":["ethereal_mediator_only","prediction_seal","ethereal_selective_law"],
  "collision_graph_gate":"HOLD_WITHOUT_FULL_KEY_TRACE"
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("claim-lattice.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-lawgen-claim-lattice-v4",
  "scientific_stage":"C3X 0.7.0-G9.4-P28",
  "constitution_sha256":cs,
  "nodes":[
   {"id":"S","requires":[]},
   {"id":"P","requires":["S"]},
   {"id":"D","requires":["P"]},
   {"id":"R","requires":["D"]},
   {"id":"HM","requires":["P"]},
   {"id":"HP","requires":["R","HM"]},
   {"id":"HX","requires":["HP"]},
   {"id":"A","requires":["HX"]},
   {"id":"G","requires":[]}
  ]
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
  "ordinal\tphase\n1\tontology_compile\n2\tportable_source_pair\n3\tprecommit\n4\tdonor\n5\trule_seal\n6\theldout_mediator\n7\tprediction_seal\n8\theldout_selective\n9\tadjudication\n").unwrap();
 println!("P28_LAWGEN_V4_PASS {} {}",ss,cs);
}
