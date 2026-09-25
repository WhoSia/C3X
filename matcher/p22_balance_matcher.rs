use std::collections::BTreeMap;
use std::env;
use std::fs;

const P:usize=9;
const Q:usize=6;
const STARTS:u64=64;
const THRESH:f64=0.50;

#[derive(Clone)]
struct Row{sha:String,family:String,side:String,square:String,z:[f64;P],tt:i64,pawnq:i64}
#[derive(Clone)]
struct Stats{n:usize,sum:[f64;P],ss:[f64;P]}
#[derive(Clone,Copy,Debug)]
struct Obj{max_smd:f64,mean_smd:f64,max_log_vr:f64}
fn better(a:Obj,b:Obj)->bool{
 let e=1e-12;
 if a.max_smd < b.max_smd-e{return true} if a.max_smd > b.max_smd+e{return false}
 if a.mean_smd < b.mean_smd-e{return true} if a.mean_smd > b.mean_smd+e{return false}
 a.max_log_vr < b.max_log_vr-e
}
fn fnv(s:&str)->u64{let mut h=14695981039346656037u64;for b in s.as_bytes(){h^=*b as u64;h=h.wrapping_mul(1099511628211);}h}
fn add(st:&mut Stats,r:&Row,sgn:f64){
 if sgn>0.0{st.n+=1}else{st.n-=1}
 for j in 0..P{st.sum[j]+=sgn*r.z[j];st.ss[j]+=sgn*r.z[j]*r.z[j];}
}
fn variance(st:&Stats,j:usize)->f64{
 if st.n<2{return 0.0}
 let n=st.n as f64;((st.ss[j]-st.sum[j]*st.sum[j]/n)/((st.n-1) as f64)).max(0.0)
}
fn objective(h:&Stats,m:&Stats)->Obj{
 let mut mx:f64=0.0;let mut sm=0.0;let mut vr:f64=0.0;
 for j in 0..P{
  let mh=h.sum[j]/h.n as f64;let mm=m.sum[j]/m.n as f64;
  let vh=variance(h,j);let vm=variance(m,j);let den=((vh+vm)/2.0).sqrt();
  let d=if den<=1e-15{if (mh-mm).abs()<1e-12{0.0}else{1e9}}else{(mh-mm).abs()/den};
  mx=mx.max(d);sm+=d;
  let lv=if vh<=1e-15&&vm<=1e-15{0.0}else if vh<=1e-15||vm<=1e-15{1e9}else{(vh/vm).ln().abs()};vr=vr.max(lv);
 }
 Obj{max_smd:mx,mean_smd:sm/P as f64,max_log_vr:vr}
}
fn parse(path:&str)->Vec<Row>{
 let txt=fs::read_to_string(path).expect("read TSV");let mut it=txt.lines();let head=it.next().expect("header");
 let want=["sha","family","side","square","sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare","inanis_tt_main","inanis_pawn_q"].join("\t");
 if head!=want{panic!("P22_TSV_HEADER_MISMATCH")}
 let mut rows=Vec::new();
 for line in it{if line.trim().is_empty(){continue}let v:Vec<&str>=line.split('\t').collect();if v.len()!=15{panic!("P22_TSV_WIDTH")}
  let mut z=[0.0;P];for j in 0..P{z[j]=v[4+j].parse().expect("feature")}
  rows.push(Row{sha:v[0].to_string(),family:v[1].to_string(),side:v[2].to_string(),square:v[3].to_string(),z,tt:v[13].parse().unwrap(),pawnq:v[14].parse().unwrap()});
 }
 rows
}
fn stats(rows:&[Row],sel:&[bool])->(Stats,Stats){
 let mut h=Stats{n:0,sum:[0.0;P],ss:[0.0;P]};let mut m=h.clone();
 for (i,r) in rows.iter().enumerate(){if !sel[i]{continue}if r.square=="HEAVY_HEAVY"{add(&mut h,r,1.0)}else if r.square=="MINOR_MINOR"{add(&mut m,r,1.0)}else{panic!("P22_SQUARE")}}
 (h,m)
}
fn selected_key(rows:&[Row],sel:&[bool])->String{let mut v:Vec<&str>=rows.iter().enumerate().filter(|(i,_)|sel[*i]).map(|(_,r)|r.sha.as_str()).collect();v.sort();v.join("|")}
fn main(){
 let a:Vec<String>=env::args().collect();if a.len()!=4{eprintln!("usage: p22_balance_matcher census.tsv selected.txt report.json");std::process::exit(2)}
 let rows=parse(&a[1]);if rows.len()<96{panic!("P22_ROW_SHORTFALL")}
 let mut strata:BTreeMap<String,Vec<usize>>=BTreeMap::new();
 for (i,r) in rows.iter().enumerate(){if r.tt<=0||r.pawnq<=0{continue}strata.entry(format!("{}|{}",r.family,r.side)).or_default().push(i);}
 if strata.len()!=16{panic!("P22_STRATA_COUNT")}
 for (k,v) in &strata{if v.len()<Q{panic!("P22_STRATUM_SHORTFALL {} {}",k,v.len())}}
 let mut best_sel:Option<Vec<bool>>=None;let mut best_obj=Obj{max_smd:1e99,mean_smd:1e99,max_log_vr:1e99};let mut best_key=String::new();let mut best_start=0;let mut best_steps=0;
 for start in 0..STARTS{
  let mut sel=vec![false;rows.len()];
  for idxs in strata.values(){let mut q=idxs.clone();q.sort_by_key(|i|(fnv(&format!("{}|{}",rows[*i].sha,start)),rows[*i].sha.clone()));for i in q.into_iter().take(Q){sel[i]=true}}
  let (mut hs,mut ms)=stats(&rows,&sel);if hs.n!=48||ms.n!=48{panic!("P22_RELATION_QUOTA")}
  let mut cur=objective(&hs,&ms);let mut steps=0;
  loop{
   let mut choice:Option<(Obj,usize,usize,Stats,Stats)>=None;
   for idxs in strata.values(){let inside:Vec<usize>=idxs.iter().copied().filter(|i|sel[*i]).collect();let outside:Vec<usize>=idxs.iter().copied().filter(|i|!sel[*i]).collect();
    for out in &inside{for inn in &outside{
     let mut h=hs.clone();let mut m=ms.clone();let st=if rows[*out].square=="HEAVY_HEAVY"{&mut h}else{&mut m};add(st,&rows[*out],-1.0);add(st,&rows[*inn],1.0);let ob=objective(&h,&m);
     let take=match &choice{None=>better(ob,cur),Some((bo,bi,boi,_,_))=>better(ob,*bo)||(!better(*bo,ob)&&!better(ob,*bo)&&(rows[*inn].sha.as_str(),rows[*out].sha.as_str())<(rows[*bi].sha.as_str(),rows[*boi].sha.as_str()))};
     if take{choice=Some((ob,*inn,*out,h,m));}
    }}
   }
   if let Some((ob,inn,out,h,m))=choice{if !better(ob,cur){break}sel[out]=false;sel[inn]=true;hs=h;ms=m;cur=ob;steps+=1;if steps>=500{break}}else{break}
  }
  let key=selected_key(&rows,&sel);if better(cur,best_obj)||(!better(best_obj,cur)&&!better(cur,best_obj)&&(best_sel.is_none()||key<best_key)){best_obj=cur;best_key=key;best_sel=Some(sel);best_start=start;best_steps=steps;}
 }
 let sel=best_sel.expect("selection");let mut shas:Vec<String>=rows.iter().enumerate().filter(|(i,_)|sel[*i]).map(|(_,r)|r.sha.clone()).collect();shas.sort();if shas.len()!=96{panic!("P22_SELECTED_COUNT")}
 fs::write(&a[2],format!("{}\n",shas.join("\n"))).expect("write selected");
 let pass=best_obj.max_smd<=THRESH+1e-12;
 let report=format!("{{\n  \"schema\": \"c3x-p22-rust-balance-search-v1\",\n  \"starts\": {},\n  \"best_start\": {},\n  \"best_steps\": {},\n  \"selected_count\": {},\n  \"max_abs_smd\": {:.17},\n  \"mean_abs_smd\": {:.17},\n  \"max_abs_log_variance_ratio\": {:.17},\n  \"threshold\": {:.2},\n  \"gate_pass\": {}\n}}\n",STARTS,best_start,best_steps,shas.len(),best_obj.max_smd,best_obj.mean_smd,best_obj.max_log_vr,THRESH,if pass{"true"}else{"false"});
 fs::write(&a[3],report).expect("write report");println!("P22_RUST_MATCHER max_smd={:.9} pass={} start={} steps={}",best_obj.max_smd,pass,best_start,best_steps);
 if !pass{std::process::exit(42)}
}
