use serde::{Deserialize,Serialize};
use serde_json::json;
use sha2::{Digest,Sha256};
use std::{collections::BTreeMap,env,fs};

#[derive(Debug,Deserialize)]
struct Doc {
    level: String,
    records: Vec<Record>,
}

#[derive(Debug,Deserialize)]
struct Record {
    event_id: String,
    source_scope: String,
    source_class: String,
    source_ply: i64,
    diagnostic: Diagnostic,
    declared_fiber_id: String,
}

#[derive(Debug,Deserialize)]
#[serde(deny_unknown_fields)]
struct Diagnostic {
    exact_continuations: i64,
    drifted_continuations: i64,
    emergent: i64,
    vanished: i64,
    first_divergence_ordinal: Option<i64>,
    emergent_by_class: [i64;4],
    vanished_by_class: [i64;4],
    drifted_by_class: [i64;4],
    count_delta_by_class: [i64;4],
}

#[derive(Debug,Serialize)]
struct Mismatch {
    event_id: String,
    declared: String,
    recomputed: String,
}

fn sign(x:i64)->i64{if x<0{-1}else if x>0{1}else{0}}
fn count_bucket(x:i64)->i64{
    let x=x.max(0);
    if x==0{0}else if x==1{1}else if x<=3{2}else if x<=7{3}else if x<=15{4}else{5}
}
fn ply_bucket(x:i64)->i64{
    if x<=0{0}else if x==1{1}else if x==2{2}else if x<=4{3}else if x<=8{4}else{5}
}
fn div_bucket(x:Option<i64>)->i64{
    match x{None=>0,Some(v) if v<=3=>1,Some(v) if v<=15=>2,Some(v) if v<=63=>3,Some(_)=>4}
}
fn cap(x:i64)->i64{x.clamp(-255,255)}
fn level_num(s:&str)->u8{
    match s{"F0"=>0,"F1"=>1,"F2"=>2,"F3"=>3,_=>panic!("bad level {}",s)}
}
fn tuple(r:&Record,level:u8)->Vec<String>{
    let d=&r.diagnostic;
    let mut v=vec![
        r.source_scope.clone(),
        r.source_class.clone(),
        ply_bucket(r.source_ply).to_string(),
        sign(d.emergent-d.vanished).to_string(),
        div_bucket(d.first_divergence_ordinal).to_string(),
    ];
    if level>=1{
        v.push(count_bucket(d.emergent).to_string());
        v.push(count_bucket(d.vanished).to_string());
        v.push(count_bucket(d.drifted_continuations).to_string());
    }
    if level>=2{
        for a in [&d.emergent_by_class,&d.vanished_by_class,&d.drifted_by_class,&d.count_delta_by_class]{
            for x in a{v.push(sign(*x).to_string());}
        }
    }
    if level>=3{
        for x in [d.exact_continuations,d.drifted_continuations,d.emergent,d.vanished]{
            v.push(cap(x).to_string());
        }
        for a in [&d.emergent_by_class,&d.vanished_by_class,&d.drifted_by_class,&d.count_delta_by_class]{
            for x in a{v.push(cap(*x).to_string());}
        }
        v.push(match d.first_divergence_ordinal{None=>"-1".into(),Some(x)=>cap(x).to_string()});
    }
    v
}
fn fiber_id(r:&Record,level:u8)->String{
    format!("F{}|{}",level,tuple(r,level).join("|"))
}
fn sha(s:&str)->String{
    let mut h=Sha256::new();h.update(s.as_bytes());format!("{:x}",h.finalize())
}

fn main(){
    let a:Vec<String>=env::args().collect();
    assert_eq!(a.len(),3,"c3x-fiber IN.json OUT.json");
    let d:Doc=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
    let level=level_num(&d.level);
    let mut mismatch=Vec::new();
    let mut members:BTreeMap<String,Vec<String>>=BTreeMap::new();
    for r in &d.records{
        let got=fiber_id(r,level);
        if got!=r.declared_fiber_id{
            mismatch.push(Mismatch{event_id:r.event_id.clone(),declared:r.declared_fiber_id.clone(),recomputed:got.clone()});
        }
        members.entry(got).or_default().push(r.event_id.clone());
    }
    for xs in members.values_mut(){xs.sort();}
    let canonical=serde_json::to_string(&members).unwrap();
    let out=json!({
        "schema":"c3x-g95-p1-fiber-verification-v1",
        "scientific_stage":"C3X 0.7.0-G9.5-P1",
        "level":d.level,
        "records":d.records.len(),
        "distinct_fibers":members.len(),
        "members":members,
        "mismatches":mismatch,
        "fiber_digest":sha(&canonical),
        "target_fields_consulted":false
    });
    fs::write(&a[2],serde_json::to_string_pretty(&out).unwrap()+"\n").unwrap();
    if !out["mismatches"].as_array().unwrap().is_empty(){std::process::exit(2);}
    println!("G95_P1_FIBER_VERIFY_PASS {} records {} fibers {}",d.level,d.records.len(),out["distinct_fibers"]);
}

#[cfg(test)]
mod tests{
    use super::*;
    fn rec()->Record{
        Record{
            event_id:"e".into(),source_scope:"MAIN".into(),source_class:"MOVE_ORDER_SEED".into(),source_ply:1,
            diagnostic:Diagnostic{
                exact_continuations:10,drifted_continuations:2,emergent:3,vanished:1,first_divergence_ordinal:Some(7),
                emergent_by_class:[1,2,0,0],vanished_by_class:[0,1,0,0],drifted_by_class:[0,1,1,0],count_delta_by_class:[1,-1,0,2]
            },
            declared_fiber_id:String::new()
        }
    }
    #[test]fn levels_refine(){let r=rec();for l in 0..4{let id=fiber_id(&r,l);assert!(id.starts_with(&format!("F{}|",l)));}}
    #[test]fn buckets_are_stable(){assert_eq!(count_bucket(0),0);assert_eq!(count_bucket(2),2);assert_eq!(div_bucket(Some(7)),2);assert_eq!(ply_bucket(1),1);}
}
