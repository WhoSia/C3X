use serde::{Deserialize,Serialize};
use serde_json::json;
use sha2::{Digest,Sha256};
use std::{collections::{BTreeMap,BTreeSet},env,fs};

#[derive(Clone,Debug,Deserialize,Serialize)]
struct Event {
    scope:String,
    #[serde(rename="class")]
    class_name:String,
    key:String,
    ply:i64,
    depth:i64,
    tt_move:u64,
    bound:i64,
    payload:i64,
    occ:i64,
    address_id:String,
    ordinal:usize,
    #[serde(default)]
    selected:i64,
    #[serde(default)]
    blocked:i64,
}
#[derive(Debug,Deserialize)]
struct Trace { events:Vec<Event> }

fn sha(s:&str)->String{let mut h=Sha256::new();h.update(s.as_bytes());format!("{:x}",h.finalize())}
fn hard(e:&Event)->String{
    format!("{}|{}|{}|{}|{}|{}|{}",e.scope,e.class_name,e.key,e.ply,e.tt_move,e.bound,e.payload)
}
fn soft_key(e:&Event)->(i64,i64,usize,String){(e.depth,e.occ,e.ordinal,e.address_id.clone())}

fn compile(base:&Trace,cf:&Trace)->serde_json::Value{
    let mut bb:BTreeMap<String,Vec<Event>>=BTreeMap::new();
    let mut cc:BTreeMap<String,Vec<Event>>=BTreeMap::new();
    for e in &base.events{bb.entry(hard(e)).or_default().push(e.clone());}
    for e in &cf.events{cc.entry(hard(e)).or_default().push(e.clone());}
    let anchors:BTreeSet<_>=bb.keys().chain(cc.keys()).cloned().collect();
    let mut pairs=Vec::new();let mut emergent=Vec::new();let mut vanished=Vec::new();
    let mut exact=0usize;let mut drift=0usize;
    for a in anchors{
        let mut b=bb.remove(&a).unwrap_or_default();let mut c=cc.remove(&a).unwrap_or_default();
        b.sort_by_key(soft_key);c.sort_by_key(soft_key);
        let n=b.len().min(c.len());
        for i in 0..n{
            let x=&b[i];let y=&c[i];let class=if x.address_id==y.address_id{"EXACT_CONTINUATION"}else{"DRIFTED_CONTINUATION"};
            if class=="EXACT_CONTINUATION"{exact+=1}else{drift+=1}
            pairs.push(json!({
                "lineage_id":sha(&format!("{}|pair|{}",a,i)),
                "class":class,"hard_anchor":a,"rank":i,
                "base_address_id":x.address_id,"counterfactual_address_id":y.address_id,
                "base_ordinal":x.ordinal,"counterfactual_ordinal":y.ordinal,
                "base_depth":x.depth,"counterfactual_depth":y.depth,
                "base_occ":x.occ,"counterfactual_occ":y.occ,
                "depth_delta":y.depth-x.depth,"occ_delta":y.occ-x.occ
            }));
        }
        for (j,e) in c.into_iter().skip(n).enumerate(){
            emergent.push(json!({"lineage_id":sha(&format!("{}|emergent|{}",a,j+n)),"class":"EMERGENT","hard_anchor":a,
                "counterfactual_address_id":e.address_id,"counterfactual_ordinal":e.ordinal,"counterfactual_depth":e.depth,"counterfactual_occ":e.occ}));
        }
        for (j,e) in b.into_iter().skip(n).enumerate(){
            vanished.push(json!({"lineage_id":sha(&format!("{}|vanished|{}",a,j+n)),"class":"VANISHED","hard_anchor":a,
                "base_address_id":e.address_id,"base_ordinal":e.ordinal,"base_depth":e.depth,"base_occ":e.occ}));
        }
    }
    pairs.sort_by_key(|x|x["counterfactual_ordinal"].as_u64().unwrap_or(u64::MAX));
    emergent.sort_by_key(|x|x["counterfactual_ordinal"].as_u64().unwrap_or(u64::MAX));
    vanished.sort_by_key(|x|x["base_ordinal"].as_u64().unwrap_or(u64::MAX));
    let mut first=None;
    let n=base.events.len().min(cf.events.len());
    for i in 0..n{
        if base.events[i].address_id!=cf.events[i].address_id{
            first=Some(json!({"ordinal":i,"kind":"TOKEN","base_address_id":base.events[i].address_id,"counterfactual_address_id":cf.events[i].address_id}));break;
        }
    }
    if first.is_none() && base.events.len()!=cf.events.len(){
        first=Some(json!({"ordinal":n,"kind":"TERMINATION","base_address_id":base.events.get(n).map(|e|e.address_id.clone()),
            "counterfactual_address_id":cf.events.get(n).map(|e|e.address_id.clone())}));
    }
    json!({
        "schema":"c3x-p33-lineage-v1",
        "algorithm":"HARD_ANCHOR_ORDER_PRESERVING_RANK_MATCH_V1",
        "hard_anchor_fields":["scope","event_type","full_key","ply","tt_move","bound","payload"],
        "soft_order":["depth","occurrence","ordinal","address_id"],
        "base_events":base.events.len(),"counterfactual_events":cf.events.len(),
        "summary":{"exact_continuations":exact,"drifted_continuations":drift,"emergent":emergent.len(),"vanished":vanished.len(),
            "matched":exact+drift},
        "pairs":pairs,"emergent":emergent,"vanished":vanished,"first_trace_divergence":first,
        "outcome_fields_consulted":false
    })
}
fn main(){
    let a:Vec<String>=env::args().collect();assert_eq!(a.len(),4,"c3x-lineage BASE.json CF.json OUT.json");
    let b:Trace=serde_json::from_str(&fs::read_to_string(&a[1]).unwrap()).unwrap();
    let c:Trace=serde_json::from_str(&fs::read_to_string(&a[2]).unwrap()).unwrap();
    fs::write(&a[3],serde_json::to_string_pretty(&compile(&b,&c)).unwrap()+"\n").unwrap();
}
#[cfg(test)]
mod tests{
 use super::*;
 fn e(depth:i64,occ:i64,addr:&str,ord:usize)->Event{Event{scope:"MAIN".into(),class_name:"MOVE_ORDER_SEED".into(),key:"aa".into(),ply:1,depth,tt_move:7,bound:1,payload:0,occ,address_id:addr.into(),ordinal:ord,selected:0,blocked:0}}
 #[test] fn exact_and_emergent(){let b=Trace{events:vec![e(5,1,"a",0)]};let c=Trace{events:vec![e(5,1,"a",0),e(6,1,"b",1)]};let x=compile(&b,&c);assert_eq!(x["summary"]["exact_continuations"],1);assert_eq!(x["summary"]["emergent"],1);}
 #[test] fn drift_is_not_emergence(){let b=Trace{events:vec![e(5,1,"a",0)]};let c=Trace{events:vec![e(6,1,"b",0)]};let x=compile(&b,&c);assert_eq!(x["summary"]["drifted_continuations"],1);assert_eq!(x["summary"]["emergent"],0);}
}
