use serde::{Deserialize,Serialize};
use serde_json::json;
use sha2::{Digest,Sha256};
use std::{collections::BTreeMap,env,fs};

#[derive(Debug,Deserialize)]
struct Doc{level:u8,events:Vec<Event>}
#[derive(Debug,Deserialize)]
struct Event{
 scope:String,class_id:i64,ply:i64,depth:i64,bound:i64,payload:i64,tt_move:u64,
 alpha:i64,beta:i64,tt_value:i64,declared:[i64;8],address_id:String,ordinal:usize
}
#[derive(Debug,Serialize,Clone,PartialEq,Eq,PartialOrd,Ord)]
struct Cone{scope:i64,class_id:i64,ply_bucket:i64,bound:i64,payload_bucket:i64,depth_bucket:i64,move_presence:i64,window_relation:i64}

fn scope(x:&str)->i64{if x=="QSEARCH"{1}else{0}}
fn plyb(x:i64)->i64{if x<=0{0}else if x==1{1}else if x==2{2}else if x<=4{3}else if x<=8{4}else{5}}
fn depthb(x:i64)->i64{if x<=0{0}else if x<=4{1}else if x<=8{2}else if x<=12{3}else if x<=16{4}else if x<=24{5}else{6}}
fn payloadb(x:i64)->i64{if x==0{0}else if x==1{1}else if x== -1{2}else if x>0{3}else{4}}
fn rel(v:i64,a:i64,b:i64)->i64{if v<=a{0}else if v>=b{2}else{1}}
fn cone(e:&Event)->Cone{Cone{scope:scope(&e.scope),class_id:e.class_id,ply_bucket:plyb(e.ply),bound:e.bound,payload_bucket:payloadb(e.payload),depth_bucket:depthb(e.depth),move_presence:if e.tt_move==0{0}else{1},window_relation:rel(e.tt_value,e.alpha,e.beta)}}
fn tuple(q:&Cone,l:u8)->Vec<i64>{
 let all=[q.scope,q.class_id,q.ply_bucket,q.bound,q.payload_bucket,q.depth_bucket,q.move_presence,q.window_relation];
 match l{0=>all[..3].to_vec(),1=>all[..5].to_vec(),2=>all[..7].to_vec(),3=>all.to_vec(),_=>panic!("bad level")}
}
fn id(t:&[i64],l:u8)->String{let body=t.iter().map(|x|x.to_string()).collect::<Vec<_>>().join(":");format!("Q{}:{}",l,body)}
fn sha(s:&str)->String{let mut h=Sha256::new();h.update(s.as_bytes());format!("{:x}",h.finalize())}

fn main(){
 let a:Vec<String>=env::args().collect();assert_eq!(a.len(),3,"c3x-cone IN.json OUT.json");
 let d:Doc=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();assert!(d.level<=3);
 let mut mismatch=Vec::new();let mut counts:BTreeMap<String,usize>=BTreeMap::new();let mut members:BTreeMap<String,Vec<String>>=BTreeMap::new();
 for e in &d.events{
  let q=cone(e);let full=[q.scope,q.class_id,q.ply_bucket,q.bound,q.payload_bucket,q.depth_bucket,q.move_presence,q.window_relation];
  if full!=e.declared{mismatch.push(json!({"ordinal":e.ordinal,"address_id":e.address_id,"declared":e.declared,"recomputed":full}));}
  let qid=id(&tuple(&q,d.level),d.level);*counts.entry(qid.clone()).or_default()+=1;members.entry(qid).or_default().push(e.address_id.clone());
 }
 let canonical=serde_json::to_string(&counts).unwrap();
 let out=json!({"schema":"c3x-p34-cone-verification-v1","level":format!("Q{}",d.level),"events":d.events.len(),
  "distinct_cones":counts.len(),"bucket_mismatches":mismatch,"counts":counts,"members":members,
  "quotient_digest":sha(&canonical),"outcome_fields_consulted":false});
 fs::write(&a[2],serde_json::to_string_pretty(&out).unwrap()+"\n").unwrap();
 if !out["bucket_mismatches"].as_array().unwrap().is_empty(){std::process::exit(2);}
 println!("P34_CONE_VERIFY_PASS Q{} events {} cones {}",d.level,d.events.len(),out["distinct_cones"]);
}

#[cfg(test)]
mod tests{
 use super::*;
 fn e()->Event{Event{scope:"MAIN".into(),class_id:1,ply:1,depth:15,bound:2,payload:0,tt_move:12,alpha:-10,beta:20,tt_value:25,declared:[0,1,1,2,0,4,1,2],address_id:"a".into(),ordinal:0}}
 #[test]fn buckets_match(){let x=e();assert_eq!(cone(&x),Cone{scope:0,class_id:1,ply_bucket:1,bound:2,payload_bucket:0,depth_bucket:4,move_presence:1,window_relation:2});}
 #[test]fn lattice_refines(){let q=cone(&e());assert_eq!(tuple(&q,0).len(),3);assert_eq!(tuple(&q,3).len(),8);}
}
