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
 let mut h=Sha256::new(); h.update(canon(v)); format!("{:x}",h.finalize())
}
fn main(){
 let a:Vec<String>=env::args().collect(); assert_eq!(a.len(),3);
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v5");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P29");
 assert_eq!(s["fresh_support"]["worlds"],128);
 assert_eq!(s["fresh_support"]["law_cells"],16);
 assert_eq!(s["fresh_support"]["history"]["measurement_nodes"],80000);
 assert_eq!(s["trace_contract"]["graph_window"],"measurement search only (search_seq=5)");
 assert_eq!(s["mediator_rule"]["heldout"],"ethereal");
 let ss=sha(&s);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v5",
  "scientific_stage":s["scientific_stage"],
  "title":s["title"],
  "spec_sha256":ss,
  "parent_authority":s["parent_authority"],
  "fresh_support":s["fresh_support"],
  "trace_contract":s["trace_contract"],
  "causal_census":s["causal_census"],
  "mediator_rule":s["mediator_rule"],
  "graph_analysis":s["graph_analysis"],
  "law_readout":s["law_readout"],
  "architecture_sources":s["architecture_sources"],
  "claim_ceiling":s["claim_ceiling"],
  "selective_outcomes_consulted":false
 });
 let cs=sha(&c);
 let out=Path::new(&a[2]); fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({
   "constitution":c,"constitution_sha256":cs
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("trace-schema.json"),serde_json::to_string_pretty(&json!({
   "schema":"c3x-p29-trace-schema-v1",
   "summary":"S,seq,probes,signature_hits,full_hits,signature_collisions,empty_signature_matches,shadow_unknown,cross_hits,origin_d1,origin_d2,origin_d3,origin_d4,origin_d5plus,store_attempts,store_commits,initial_stores,same_key_updates,replacements,store_rejects,age_attempts,age_changes,age_true_key,age_collision_key",
   "replacement":"R,seq,bucket,slot,old_key,new_key,old_store_seq",
   "signature_collision":"C,seq,bucket,slot,requested_key,resident_key,resident_store_seq",
   "age_write":"A,seq,bucket,slot,requested_key,resident_key,value_changed",
   "graph_seq":5
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
  "ordinal\tphase\n1\tontology_compile\n2\ttrace_materialization\n3\tfresh_support_precommit\n4\tdonor_trace_and_law\n5\tdonor_mediator_rule\n6\theldout_trace_only\n7\theldout_prediction_seal\n8\theldout_selective_law\n9\tadjudication\n").unwrap();
 println!("P29_LAWGEN_V5_PASS {} {}",ss,cs);
}
