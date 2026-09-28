use clap::{Parser,Subcommand};
use serde_json::{json,Map,Value};
use std::{collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P8";
const EPS:f64=1e-12;

#[derive(Parser)]
#[command(name="c3x-prototype-p8")]
struct Cli{#[command(subcommand)]cmd:Cmd}
#[derive(Subcommand)]
enum Cmd{
 Cover{#[arg(long)]profiles:PathBuf,#[arg(long)]law:PathBuf,#[arg(long)]out:PathBuf},
 Query{#[arg(long)]index:PathBuf,#[arg(long)]profiles:PathBuf,#[arg(long)]out:PathBuf},
}

fn load(p:&PathBuf)->Value{serde_json::from_str(&fs::read_to_string(p).unwrap()).unwrap()}
fn save(p:&PathBuf,v:&Value){if let Some(q)=p.parent(){fs::create_dir_all(q).unwrap();}fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();}
fn s<'a>(v:&'a Value,k:&str)->&'a str{v[k].as_str().unwrap_or("")}
fn block_keys(law:&Value)->Vec<(String,f64,Vec<String>)>{
 let mut out=Vec::new();
 let blocks=law["descriptor"]["blocks"].as_object().unwrap();
 for (name,z) in blocks{
  let w=z["weight"].as_f64().unwrap();
  let fs=z["features"].as_array().unwrap().iter().map(|x|x.as_str().unwrap().to_string()).collect();
  out.push((name.clone(),w,fs));
 }
 out.sort_by(|a,b|a.0.cmp(&b.0));out
}
fn dist_desc(a:&Value,b:&Value,blocks:&[(String,f64,Vec<String>)])->f64{
 let mut total=0.0;
 for (name,w,keys) in blocks{
  let aa=&a[name];let bb=&b[name];let mut mis=0usize;
  for k in keys{if aa[k]!=bb[k]{mis+=1;}}
  total += *w * (mis as f64)/(keys.len() as f64);
 }
 total
}
fn records<'a>(p:&'a Value)->Vec<&'a Value>{
 let mut xs:Vec<&Value>=p["records"].as_array().unwrap().iter().collect();
 xs.sort_by(|a,b|s(a,"record_id").cmp(s(b,"record_id")));xs
}
fn matrix(xs:&[&Value],blocks:&[(String,f64,Vec<String>)])->Vec<Vec<f64>>{
 let n=xs.len();let mut m=vec![vec![0.0;n];n];
 for i in 0..n{for j in i+1..n{let d=dist_desc(&xs[i]["descriptor"],&xs[j]["descriptor"],blocks);m[i][j]=d;m[j][i]=d;}}m
}
fn farthest_cover(xs:&[&Value],m:&[Vec<f64>],radius:f64)->Vec<usize>{
 assert!(!xs.is_empty());let n=xs.len();let mut ps=vec![0usize];let mut in_p=vec![false;n];in_p[0]=true;
 loop{
  let mut best:Option<(usize,f64)>=None;
  for i in 0..n{
   if in_p[i]{continue}
   let nd=ps.iter().map(|&p|m[i][p]).fold(f64::INFINITY,f64::min);
   match best{
    None=>best=Some((i,nd)),
    Some((bi,bd))=>{
     if nd>bd+EPS || ((nd-bd).abs()<=EPS && s(xs[i],"record_id")<s(xs[bi],"record_id")){best=Some((i,nd));}
    }
   }
  }
  let Some((i,d))=best else{break};
  if d<=radius+EPS{break}
  ps.push(i);in_p[i]=true;
 }
 ps.sort_by(|&a,&b|s(xs[a],"record_id").cmp(s(xs[b],"record_id")));ps
}
fn assign(xs:&[&Value],m:&[Vec<f64>],ps:&[usize])->Vec<(usize,f64)>{
 let mut out=Vec::new();
 for i in 0..xs.len(){
  let mut best=(ps[0],m[i][ps[0]]);
  for &p in &ps[1..]{
   let d=m[i][p];
   if d<best.1-EPS || ((d-best.1).abs()<=EPS && s(xs[p],"record_id")<s(xs[best.0],"record_id")){best=(p,d);}
  }
  out.push(best)
 }out
}
fn metrics(xs:&[&Value],ps:&[usize],asgn:&[(usize,f64)])->Value{
 let n=xs.len();let mut groups:BTreeMap<usize,Vec<usize>>=BTreeMap::new();
 for (i,(p,_)) in asgn.iter().enumerate(){groups.entry(*p).or_default().push(i);}
 let reused:usize=groups.values().filter(|v|v.len()>1).map(|v|v.len()).sum();
 let mut xp=0usize;let mut xe=0usize;let mut maxs=0usize;
 for v in groups.values(){
  maxs=maxs.max(v.len());
  let pos:BTreeSet<&str>=v.iter().map(|&i|s(xs[i],"position_id")).collect();
  let eng:BTreeSet<&str>=v.iter().map(|&i|s(xs[i],"engine")).collect();
  if pos.len()>1{xp+=v.len()} if eng.len()>1{xe+=v.len()}
 }
 json!({"records":n,"prototypes":ps.len(),"compression":1.0-(ps.len() as f64)/(n as f64),
  "reused_records":reused,"cross_position_reused_records":xp,"cross_engine_reused_records":xe,
  "max_prototype_support":maxs,"max_prototype_fraction":(maxs as f64)/(n as f64)})
}
fn pass(m:&Value,g:&Value)->bool{
 m["compression"].as_f64().unwrap()+EPS>=g["min_compression"].as_f64().unwrap()
 && m["compression"].as_f64().unwrap()<=g["max_compression"].as_f64().unwrap()+EPS
 && m["reused_records"].as_u64().unwrap()>=g["min_reused_records"].as_u64().unwrap()
 && m["cross_position_reused_records"].as_u64().unwrap()>=g["min_cross_position_reused_records"].as_u64().unwrap()
 && m["cross_engine_reused_records"].as_u64().unwrap()>=g["min_cross_engine_reused_records"].as_u64().unwrap()
 && m["max_prototype_fraction"].as_f64().unwrap()<=g["max_prototype_fraction"].as_f64().unwrap()+EPS
}
fn cover(profiles:PathBuf,lawp:PathBuf,out:PathBuf){
 let p=load(&profiles);let law=load(&lawp);
 assert_eq!(p["scientific_stage"],STAGE);assert_eq!(p["target_fields_consulted"],false);
 assert_eq!(p["counterfactual_information_consulted"],false);assert_eq!(p["p7_q_state_consulted"],false);
 assert_eq!(law["schema"],"c3x-p8-prototype-law-v1");
 let xs=records(&p);let blocks=block_keys(&law);let m=matrix(&xs,&blocks);
 let radii=law["prototype_cover"]["radius_ladder"].as_array().unwrap();
 let gate=&law["prototype_cover"]["engineering_gate"];let mut evals=Vec::new();let mut chosen:Option<(f64,Vec<usize>,Vec<(usize,f64)>,Value)>=None;
 for rv in radii{
  let r=rv.as_f64().unwrap();let ps=farthest_cover(&xs,&m,r);let a=assign(&xs,&m,&ps);let mt=metrics(&xs,&ps,&a);let ok=pass(&mt,gate);
  evals.push(json!({"radius":r,"metrics":mt,"pass":ok}));
  if chosen.is_none()&&ok{chosen=Some((r,ps,a,evals.last().unwrap()["metrics"].clone()));}
 }
 let mut proto=Vec::new();let mut assignments=Vec::new();let mut selected_radius=Value::Null;let mut status="NO_TARGET_BLIND_PROTOTYPE_COVER";
 if let Some((r,ps,a,_mt))=chosen{
  selected_radius=json!(r);status="TARGET_BLIND_PROTOTYPE_COVER_SELECTED";
  let mut groups:BTreeMap<usize,Vec<usize>>=BTreeMap::new();for (i,(q,_)) in a.iter().enumerate(){groups.entry(*q).or_default().push(i);}
  for &q in &ps{
   let id=format!("P8P:{}",s(xs[q],"record_id"));
   let members=&groups[&q];
   proto.push(json!({"prototype_id":id,"medoid_record_id":s(xs[q],"record_id"),"descriptor":xs[q]["descriptor"],
    "profile_support":members.len(),"engines":members.iter().map(|&i|s(xs[i],"engine")).collect::<BTreeSet<_>>(),
    "positions":members.iter().map(|&i|s(xs[i],"position_id")).collect::<BTreeSet<_>>()}));
  }
  let idmap:BTreeMap<usize,String>=ps.iter().map(|&q|(q,format!("P8P:{}",s(xs[q],"record_id")))).collect();
  for (i,(q,d)) in a.iter().enumerate(){assignments.push(json!({"record_id":s(xs[i],"record_id"),"prototype_id":idmap[q],"distance":d}));}
 }
 let z=json!({"schema":"c3x-p8-prototype-index-v1","scientific_stage":STAGE,"status":status,
  "descriptor_family":"RATE_SHAPE_SCALE","selected_radius":selected_radius,"radius_evaluations":evals,
  "prototypes":proto,"assignments":assignments,"target_fields_consulted":false,"counterfactual_information_consulted":false,
  "p7_q_state_consulted":false,"post_target_metric_refit":false});
 save(&out,&z);println!("P8_PROTO_COVER {} {} {}",status,xs.len(),z["prototypes"].as_array().unwrap().len());
}
fn query(index:PathBuf,profiles:PathBuf,out:PathBuf){
 let idx=load(&index);let p=load(&profiles);assert_eq!(idx["schema"],"c3x-p8-prototype-index-v1");
 assert_eq!(p["target_fields_consulted"],false);assert_eq!(p["counterfactual_information_consulted"],false);
 let r=idx["selected_radius"].as_f64();let mut rows=Vec::new();
 if r.is_none(){
  for q in p["records"].as_array().unwrap(){rows.push(json!({"record_id":q["record_id"],"status":"ABSTAIN_NO_PROTOTYPE_INDEX","prototype_id":Value::Null,"distance":Value::Null}));}
 }else{
  let r=r.unwrap();let blocks:Vec<(String,f64,Vec<String>)>=vec![
   ("board".into(),0.15,vec!["side_to_move","in_check","phase","legal_moves_bucket","material_balance_bucket","castling_bucket","halfmove_bucket"].into_iter().map(String::from).collect()),
   ("current_event".into(),0.30,vec!["scope","class","ply_bucket","depth_bucket","bound_bucket","window_relation","move_presence","payload_bucket"].into_iter().map(String::from).collect()),
   ("provenance_rates".into(),0.30,vec!["cutoff_share","move_order_share","eval_share","pv_share","qsearch_share","current_scope_share","current_class_share","unique_key_ratio","repeated_key_event_share","current_key_share","same_key_gap_ratio","same_class_gap_ratio","depth_percentile","same_ply_share"].into_iter().map(String::from).collect()),
   ("temporal_shape".into(),0.20,vec!["q1_class","q1_scope","q1_reuse","q2_class","q2_scope","q2_reuse","q3_class","q3_scope","q3_reuse","q4_class","q4_scope","q4_reuse"].into_iter().map(String::from).collect()),
   ("coarse_scale".into(),0.05,vec!["prefix_size_bucket"].into_iter().map(String::from).collect())];
  let ps=idx["prototypes"].as_array().unwrap();
  for q in p["records"].as_array().unwrap(){
   let mut best:Option<(&Value,f64)>=None;
   for z in ps{
    let d=dist_desc(&q["descriptor"],&z["descriptor"],&blocks);
    match best{None=>best=Some((z,d)),Some((b,bd))=>if d<bd-EPS||((d-bd).abs()<=EPS&&s(z,"prototype_id")<s(b,"prototype_id")){best=Some((z,d));}}
   }
   let (z,d)=best.unwrap();let covered=d<=r+EPS;
   rows.push(json!({"record_id":q["record_id"],"status":if covered{"COVERED"}else{"ABSTAIN_OUTSIDE_RADIUS"},
    "prototype_id":if covered{z["prototype_id"].clone()}else{Value::Null},"distance":d}));
  }
 }
 save(&out,&json!({"schema":"c3x-p8-prototype-query-v1","scientific_stage":STAGE,"selected_radius":idx["selected_radius"],
  "queries":rows,"target_fields_consulted":false,"counterfactual_information_consulted":false,"post_target_metric_refit":false}));
 println!("P8_PROTO_QUERY {}",p["records"].as_array().unwrap().len());
}
fn main(){let c=Cli::parse();match c.cmd{Cmd::Cover{profiles,law,out}=>cover(profiles,law,out),Cmd::Query{index,profiles,out}=>query(index,profiles,out)}}
