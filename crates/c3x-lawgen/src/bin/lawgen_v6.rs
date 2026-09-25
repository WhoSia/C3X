use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{env,fs,path::Path};

fn canon(v:&Value)->Vec<u8>{
 let mut x=v.clone();
 fn sort(v:&mut Value){match v{
  Value::Object(m)=>{let old=std::mem::take(m);let mut kv:Vec<_>=old.into_iter().collect();kv.sort_by(|a,b|a.0.cmp(&b.0));for(k,mut z)in kv{sort(&mut z);m.insert(k,z);}},
  Value::Array(a)=>for z in a{sort(z)}, _=>{}
 }}
 sort(&mut x);serde_json::to_vec(&x).unwrap()
}
fn sha(v:&Value)->String{let mut h=Sha256::new();h.update(canon(v));format!("{:x}",h.finalize())}
fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3);
 let s:Value=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
 assert_eq!(s["schema"],"c3x-lawgen-spec-v6");
 assert_eq!(s["scientific_stage"],"C3X 0.7.0-G9.4-P30");
 assert_eq!(s["support"]["pressure_probe_worlds"],16);
 assert_eq!(s["support"]["law_worlds"],128);
 assert_eq!(s["support"]["law_capacity_mib"],1);
 assert_eq!(s["support"]["capacities_mib"],json!([1,4,16,64]));
 let ss=sha(&s);
 let c=json!({
  "schema":"c3x-lawgen-constitution-v6",
  "scientific_stage":s["scientific_stage"],"title":s["title"],"spec_sha256":ss,
  "parent_authority":s["parent_authority"],"objective":s["objective"],"support":s["support"],
  "victim_instrument":s["victim_instrument"],"causal_chain":s["causal_chain"],
  "mediator_rule":s["mediator_rule"],"explanation_certificate":s["explanation_certificate"],
  "architecture_sources":s["architecture_sources"],"literature_anchor":s["literature_anchor"],
  "claim_ceiling":s["claim_ceiling"],"heldout_selective_consulted":false
 });
 let cs=sha(&c);let out=Path::new(&a[2]);fs::create_dir_all(out).unwrap();
 fs::write(out.join("constitution.json"),serde_json::to_string_pretty(&json!({"constitution":c,"constitution_sha256":cs})).unwrap()+"\n").unwrap();
 fs::write(out.join("explanation-contract.json"),serde_json::to_string_pretty(&json!({
  "schema":"c3x-p30-explanation-contract-v1",
  "labels":["NULL_BEFORE_VICTIM","VICTIM_ONLY","REPLACEMENT_EDGE","REUSE_EDGE","SEARCH_EFFECT","LAW_EFFECT"],
  "template":"At {hash_mib} MiB, age-on-hit changed victim eligibility by {victim_delta}; committed replacements changed by {replacement_delta}; protected-then-reused keys changed by {protected_reuse_delta}; full-key reuse changed by {full_hit_delta}; law mask={law_mask}.",
  "authority":"verbalize measured fields only"
 })).unwrap()+"\n").unwrap();
 fs::write(out.join("execution-matrix.tsv"),
 "ordinal\tphase\n1\tcompile_constitution\n2\tbuild_trace_variants\n3\tprecommit\n4\tpressure_trace_1_4_16_64\n5\tdonor_1mib_law\n6\tdonor_rule\n7\theldout_prediction\n8\theldout_1mib_law\n9\texplanation_certificate_adjudication\n").unwrap();
 println!("P30_LAWGEN_V6_PASS {} {}",ss,cs);
}
