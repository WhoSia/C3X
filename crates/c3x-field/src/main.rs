use clap::{Parser,Subcommand};
use serde::{Deserialize,Serialize};
use serde_json::{json,Value};
use sha2::{Digest,Sha256};
use std::{collections::{BTreeMap,BTreeSet},fs,path::PathBuf};

const STAGE:&str="C3X 0.7.0-G9.5-P2";

#[derive(Parser,Debug)]
#[command(name="c3x-field",version,about="Discover, scope, query and verify context-indexed causal-fiber fields")]
struct Cli{#[command(subcommand)] command:Command}

#[derive(Subcommand,Debug)]
enum Command{
    Discover{
        #[arg(long)] constitution:PathBuf,
        #[arg(long)] input:PathBuf,
        #[arg(long)] out:PathBuf,
    },
    Scope{
        #[arg(long)] discovery:PathBuf,
        #[arg(long)] profiles:PathBuf,
        #[arg(long)] out:PathBuf,
    },
    Verify{
        #[arg(long)] scope:PathBuf,
        #[arg(long)] targets:PathBuf,
        #[arg(long)] out:PathBuf,
    },
    Query{
        #[arg(long)] discovery:PathBuf,
        #[arg(long)] basis:String,
        #[arg(long)] profiles:PathBuf,
        #[arg(long)] out:PathBuf,
    },
}

#[derive(Clone,Debug,Deserialize,Serialize)]
#[serde(deny_unknown_fields)]
struct DiscoveryRecord{
    record_id:String,
    engine:String,
    position_id:String,
    event_id:String,
    fiber_id:String,
    context:BTreeMap<String,String>,
    architecture_context:BTreeMap<String,String>,
    target:bool,
}

#[derive(Debug,Deserialize)]
#[serde(deny_unknown_fields)]
struct DiscoveryInput{
    schema:String,
    scientific_stage:String,
    portable_coordinates:Vec<String>,
    architecture_coordinates:Vec<String>,
    records:Vec<DiscoveryRecord>,
}

#[derive(Clone,Debug,Deserialize,Serialize)]
#[serde(deny_unknown_fields)]
struct ProfileRecord{
    record_id:String,
    engine:String,
    position_id:String,
    event_id:String,
    fiber_id:String,
    context:BTreeMap<String,String>,
    architecture_context:BTreeMap<String,String>,
}

#[derive(Debug,Deserialize)]
#[serde(deny_unknown_fields)]
struct ProfileBatch{
    schema:String,
    scientific_stage:String,
    records:Vec<ProfileRecord>,
}

#[derive(Debug,Deserialize)]
struct TargetRecord{
    record_id:String,
    root_change:bool,
    #[serde(default)]
    parent_bestmove:Option<String>,
    #[serde(default)]
    counterfactual_bestmove:Option<String>,
    #[serde(flatten)]
    extra:BTreeMap<String,Value>,
}

#[derive(Debug,Deserialize)]
#[serde(deny_unknown_fields)]
struct TargetBatch{
    schema:String,
    scientific_stage:String,
    records:Vec<TargetRecord>,
}

fn read_json(p:&PathBuf)->Value{
    serde_json::from_str(&fs::read_to_string(p).unwrap_or_else(|e|panic!("read {}: {e}",p.display())))
        .unwrap_or_else(|e|panic!("json {}: {e}",p.display()))
}
fn sha_value(v:&Value)->String{
    let mut x=v.clone();
    fn sort(v:&mut Value){match v{
        Value::Object(m)=>{
            let old=std::mem::take(m);let mut kv:Vec<_>=old.into_iter().collect();
            kv.sort_by(|a,b|a.0.cmp(&b.0));
            for(k,mut z)in kv{sort(&mut z);m.insert(k,z);}
        },
        Value::Array(a)=>for z in a{sort(z)},_=>{}
    }}
    sort(&mut x);
    let mut h=Sha256::new();h.update(serde_json::to_vec(&x).unwrap());format!("{:x}",h.finalize())
}
fn write_json(p:&PathBuf,v:&Value){
    if let Some(par)=p.parent(){fs::create_dir_all(par).unwrap();}
    fs::write(p,serde_json::to_string_pretty(v).unwrap()+"\n").unwrap();
}
fn int_at(v:&Value,path:&[&str])->usize{
    let mut z=v;for k in path{z=&z[*k];}
    z.as_u64().unwrap_or_else(||panic!("int {:?}",path)) as usize
}
fn f64_at(v:&Value,path:&[&str])->f64{
    let mut z=v;for k in path{z=&z[*k];}
    z.as_f64().unwrap_or_else(||panic!("float {:?}",path))
}
fn bool_at(v:&Value,path:&[&str])->bool{
    let mut z=v;for k in path{z=&z[*k];}
    z.as_bool().unwrap_or_else(||panic!("bool {:?}",path))
}
fn combinations(items:&[String],k:usize)->Vec<Vec<String>>{
    fn rec(items:&[String],k:usize,start:usize,cur:&mut Vec<String>,out:&mut Vec<Vec<String>>){
        if cur.len()==k{out.push(cur.clone());return;}
        for i in start..items.len(){
            cur.push(items[i].clone());rec(items,k,i+1,cur,out);cur.pop();
        }
    }
    if k==0{return vec![vec![]]}
    let mut out=Vec::new();rec(items,k,0,&mut Vec::new(),&mut out);out
}
fn basis_id(coords:&[String])->String{
    if coords.is_empty(){"P:EMPTY".into()}
    else if coords.iter().any(|x|x.starts_with("arch:")){format!("A:{}",coords.join("+"))}
    else{format!("P:{}",coords.join("+"))}
}
fn rec_value(r:&DiscoveryRecord,c:&str)->String{
    if let Some(k)=c.strip_prefix("arch:"){r.architecture_context.get(k).unwrap_or_else(||panic!("missing arch {k}")).clone()}
    else{r.context.get(c).unwrap_or_else(||panic!("missing context {c}")).clone()}
}
fn prof_value(r:&ProfileRecord,c:&str)->String{
    if let Some(k)=c.strip_prefix("arch:"){r.architecture_context.get(k).unwrap_or_else(||panic!("missing arch {k}")).clone()}
    else{r.context.get(c).unwrap_or_else(||panic!("missing context {c}")).clone()}
}
fn cell_key_parts(fiber:&str,vals:Vec<(String,String)>)->String{
    let mut parts=vec![fiber.to_string()];
    for(k,v)in vals{parts.push(format!("{k}={v}"));}
    parts.join("||")
}
fn cell_key_record(r:&DiscoveryRecord,coords:&[String])->String{
    cell_key_parts(&r.fiber_id,coords.iter().map(|c|(c.clone(),rec_value(r,c))).collect())
}
fn cell_key_profile(r:&ProfileRecord,coords:&[String])->String{
    cell_key_parts(&r.fiber_id,coords.iter().map(|c|(c.clone(),prof_value(r,c))).collect())
}

#[derive(Clone,Debug)]
struct Metrics{
    records:usize,
    distinct_cells:usize,
    collisions:usize,
    compression:f64,
    cross_position_records:usize,
    cross_engine_records:usize,
    positives:usize,
    negatives:usize,
}
fn metrics(records:&[DiscoveryRecord],coords:&[String])->Metrics{
    let mut g:BTreeMap<String,Vec<&DiscoveryRecord>>=BTreeMap::new();
    for r in records{g.entry(cell_key_record(r,coords)).or_default().push(r);}
    let mut collisions=0;let mut crossp=0;let mut crosse=0;
    for rs in g.values(){
        let labs:BTreeSet<bool>=rs.iter().map(|r|r.target).collect();
        if labs.len()>1{collisions+=1;}
        let ps:BTreeSet<&str>=rs.iter().map(|r|r.position_id.as_str()).collect();
        if ps.len()>=2{crossp+=rs.len();}
        let es:BTreeSet<&str>=rs.iter().map(|r|r.engine.as_str()).collect();
        if es.len()>=2{crosse+=rs.len();}
    }
    let n=records.len();let d=g.len();
    Metrics{
        records:n,distinct_cells:d,collisions,
        compression:if n==0{0.0}else{1.0-d as f64/n as f64},
        cross_position_records:crossp,cross_engine_records:crosse,
        positives:records.iter().filter(|r|r.target).count(),
        negatives:records.iter().filter(|r|!r.target).count(),
    }
}
fn metrics_json(m:&Metrics)->Value{json!({
    "records":m.records,"distinct_cells":m.distinct_cells,"target_collisions":m.collisions,
    "compression":m.compression,"cross_position_records":m.cross_position_records,
    "cross_engine_records":m.cross_engine_records,"positive_records":m.positives,"negative_records":m.negatives
})}
fn field_cells(records:&[DiscoveryRecord],coords:&[String])->Value{
    let mut g:BTreeMap<String,Vec<&DiscoveryRecord>>=BTreeMap::new();
    for r in records{g.entry(cell_key_record(r,coords)).or_default().push(r);}
    let mut out=serde_json::Map::new();
    for(k,rs)in g{
        let labs:BTreeSet<bool>=rs.iter().map(|r|r.target).collect();
        let label=if labs.len()==1{Some(*labs.iter().next().unwrap())}else{None};
        let engines:BTreeSet<String>=rs.iter().map(|r|r.engine.clone()).collect();
        let positions:BTreeSet<String>=rs.iter().map(|r|r.position_id.clone()).collect();
        let ids:Vec<String>=rs.iter().map(|r|r.record_id.clone()).collect();
        out.insert(k,json!({
            "label":label.map(|b|if b{"ROOT_CHANGE"}else{"NO_ROOT_CHANGE"}),
            "support":rs.len(),"engines":engines,"positions":positions,"record_ids":ids
        }));
    }
    Value::Object(out)
}
fn assess_pass(m:&Metrics,min_comp:f64,min_cp:usize,min_ce:usize,require_both:bool)->bool{
    m.collisions==0 && m.compression+1e-12>=min_comp &&
    m.cross_position_records>=min_cp && m.cross_engine_records>=min_ce &&
    (!require_both || (m.positives>0 && m.negatives>0))
}
fn make_basis_cert(records:&[DiscoveryRecord],coords:Vec<String>,pass:bool)->Value{
    let m=metrics(records,&coords);let card=coords.len();let cells=if pass{field_cells(records,&coords)}else{json!({})};
    json!({"basis_id":basis_id(&coords),"coordinates":coords,"cardinality":card,
        "metrics":metrics_json(&m),"admissible":pass,"cells":cells})
}
fn validate_context(records:&[DiscoveryRecord],portable:&[String],arch:&[String]){
    for r in records{
        for c in portable{assert!(r.context.contains_key(c),"missing portable {} {}",c,r.record_id);}
        for c in arch{assert!(r.architecture_context.contains_key(c),"missing architecture {} {}",c,r.record_id);}
    }
}
fn discovery_command(constitution:PathBuf,input:PathBuf,out:PathBuf){
    let cw=read_json(&constitution);let c=&cw["constitution"];
    assert_eq!(c["schema"],"c3x-lawgen-constitution-v12");
    assert_eq!(c["scientific_stage"],STAGE);
    let iv=read_json(&input);let d:DiscoveryInput=serde_json::from_value(iv.clone()).unwrap();
    assert_eq!(d.schema,"c3x-field-discovery-input-v1");assert_eq!(d.scientific_stage,STAGE);
    // constitution portable entries are objects; read their frozen names directly.
    let portable:Vec<String>=c["context_vocabulary"]["portable"].as_array().unwrap().iter()
        .map(|x|x["name"].as_str().unwrap().to_string()).collect();
    let arch:Vec<String>=c["context_vocabulary"]["architecture_secondary"].as_array().unwrap()
        .iter().map(|x|x.as_str().unwrap().to_string()).collect();
    assert_eq!(d.portable_coordinates,portable);assert_eq!(d.architecture_coordinates,arch);
    validate_context(&d.records,&portable,&arch);

    let min_n=int_at(c,&["discovery_basis_court","support_gate","min_fired_records"]);
    let min_pos=int_at(c,&["discovery_basis_court","support_gate","min_positive_records"]);
    let min_neg=int_at(c,&["discovery_basis_court","support_gate","min_negative_records"]);
    let n=d.records.len();let pos=d.records.iter().filter(|r|r.target).count();let neg=n-pos;
    let support_pass=n>=min_n&&pos>=min_pos&&neg>=min_neg;

    let maxk=int_at(c,&["discovery_basis_court","max_portable_cardinality"]);
    let min_comp=f64_at(c,&["discovery_basis_court","admissibility","min_compression"]);
    let min_cp=int_at(c,&["discovery_basis_court","admissibility","min_records_in_cross_position_cells"]);
    let min_ce=int_at(c,&["discovery_basis_court","admissibility","min_records_in_cross_engine_cells"]);
    let require_both=bool_at(c,&["discovery_basis_court","admissibility","require_both_target_labels"]);

    let mut census=Vec::new();let mut minimal=Vec::new();let mut min_card:Option<usize>=None;
    if support_pass{
        for k in 0..=maxk{
            let mut at_k=Vec::new();
            for coords in combinations(&portable,k){
                let m=metrics(&d.records,&coords);
                let pass=assess_pass(&m,min_comp,min_cp,min_ce,require_both);
                census.push(json!({"basis_id":basis_id(&coords),"coordinates":coords,"cardinality":k,
                    "metrics":metrics_json(&m),"admissible":pass}));
                if pass{at_k.push(coords);}
            }
            if !at_k.is_empty(){min_card=Some(k);for coords in at_k{minimal.push(make_basis_cert(&d.records,coords,true));}break;}
        }
    }

    let mut engine_specific=serde_json::Map::new();
    let eg=&c["discovery_basis_court"]["engine_specific_admissibility"];
    let es_min_n=eg["support_gate"]["min_fired_records"].as_u64().unwrap() as usize;
    let es_min_pos=eg["support_gate"]["min_positive_records"].as_u64().unwrap() as usize;
    let es_min_neg=eg["support_gate"]["min_negative_records"].as_u64().unwrap() as usize;
    let es_comp=eg["min_compression"].as_f64().unwrap();
    let es_cp=eg["min_records_in_cross_position_cells"].as_u64().unwrap() as usize;
    let es_max=eg["max_portable_cardinality"].as_u64().unwrap() as usize;
    let engines:BTreeSet<String>=d.records.iter().map(|r|r.engine.clone()).collect();
    for e in engines{
        let rr:Vec<DiscoveryRecord>=d.records.iter().filter(|r|r.engine==e).cloned().collect();
        let ep=rr.iter().filter(|r|r.target).count();let en=rr.len()-ep;
        let esp=rr.len()>=es_min_n&&ep>=es_min_pos&&en>=es_min_neg;
        let mut mins=Vec::new();let mut mc=None;
        if esp{
            for k in 0..=es_max{
                let mut found=Vec::new();
                for coords in combinations(&portable,k){
                    let m=metrics(&rr,&coords);
                    let pass=m.collisions==0&&m.compression+1e-12>=es_comp&&m.cross_position_records>=es_cp&&m.positives>0&&m.negatives>0;
                    if pass{found.push(coords);}
                }
                if !found.is_empty(){mc=Some(k);for coords in found{mins.push(make_basis_cert(&rr,coords,true));}break;}
            }
        }
        engine_specific.insert(e,json!({"support_pass":esp,"minimum_cardinality":mc,"minimal_bases":mins}));
    }

    let mut arch_diag=Vec::new();
    if support_pass&&minimal.is_empty(){
        let ag=&c["discovery_basis_court"]["architecture_diagnostic"];
        let max_total=ag["max_total_cardinality"].as_u64().unwrap() as usize;
        let arch_names:Vec<String>=arch.iter().map(|x|format!("arch:{x}")).collect();
        'outer:for total in 2..=max_total{
            let mut found=Vec::new();
            // exactly one architecture coordinate and at least one portable coordinate.
            for a0 in &arch_names{
                for pcoords in combinations(&portable,total-1){
                    let mut coords=pcoords;coords.push(a0.clone());coords.sort();
                    let m=metrics(&d.records,&coords);
                    if assess_pass(&m,min_comp,min_cp,min_ce,require_both){found.push(coords);}
                }
            }
            if !found.is_empty(){for coords in found{arch_diag.push(make_basis_cert(&d.records,coords,true));}break 'outer;}
        }
    }

    let status=if !support_pass{"DISCOVERY_SUPPORT_LIMITED"}else if minimal.is_empty(){"NO_PORTABLE_BASIS_HOLD"}else{"PORTABLE_MINIMAL_BASIS_FRONTIER"};
    let scope_gate=c["heldout_firewall"]["pre_target_scope_gate"].clone();
    let outv=json!({
        "schema":"c3x-field-discovery-v1","scientific_stage":STAGE,"status":status,
        "constitution_sha256":cw["constitution_sha256"],"input_sha256":sha_value(&iv),
        "support":{"records":n,"positive_records":pos,"negative_records":neg,"pass":support_pass},
        "portable_coordinates":portable,"architecture_coordinates":arch,
        "minimum_portable_cardinality":min_card,"minimal_portable_bases":minimal,
        "portable_search_census":census,"architecture_diagnostic_bases":arch_diag,
        "engine_specific":engine_specific,"heldout_scope_gate":scope_gate,
        "target_fields_consulted":true,
        "authority_ceiling":"Discovery outcomes identify a finite minimal context-basis frontier only; held-out targets have not been consulted."
    });
    write_json(&out,&outv);
    println!("C3X_FIELD_DISCOVER {} records {} positives {} minimal {}",status,n,pos,outv["minimal_portable_bases"].as_array().unwrap().len());
}

fn basis_lookup<'a>(discovery:&'a Value,bid:&str)->&'a Value{
    discovery["minimal_portable_bases"].as_array().unwrap().iter()
        .find(|b|b["basis_id"].as_str()==Some(bid))
        .unwrap_or_else(||panic!("basis not found {bid}"))
}
fn scope_eval(b:&Value,profiles:&[ProfileRecord])->(usize,BTreeSet<String>,BTreeSet<String>,usize,Vec<Value>){
    let coords:Vec<String>=b["coordinates"].as_array().unwrap().iter().map(|x|x.as_str().unwrap().to_string()).collect();
    let cells=b["cells"].as_object().unwrap();
    let mut seen=0;let mut engines=BTreeSet::new();let mut positions=BTreeSet::new();let mut pospred=0;let mut preds=Vec::new();
    for p in profiles{
        let key=cell_key_profile(p,&coords);
        if let Some(c)=cells.get(&key){
            seen+=1;engines.insert(p.engine.clone());positions.insert(p.position_id.clone());
            let lab=c["label"].as_str().unwrap();if lab=="ROOT_CHANGE"{pospred+=1;}
            preds.push(json!({"record_id":p.record_id,"engine":p.engine,"position_id":p.position_id,"event_id":p.event_id,
                "fiber_id":p.fiber_id,"cell_key":key,"status":if lab=="ROOT_CHANGE"{"CERTIFIED_ROOT_CHANGE"}else{"CERTIFIED_NO_ROOT_CHANGE"},
                "predicted_root_change":lab=="ROOT_CHANGE","discovery_support":c["support"]}));
        }else{
            preds.push(json!({"record_id":p.record_id,"engine":p.engine,"position_id":p.position_id,"event_id":p.event_id,
                "fiber_id":p.fiber_id,"cell_key":key,"status":"ABSTAIN_UNSEEN_CONTEXT","predicted_root_change":Value::Null,"discovery_support":0}));
        }
    }
    (seen,engines,positions,pospred,preds)
}
fn read_profiles(path:&PathBuf)->(Value,ProfileBatch){
    let v=read_json(path);let p:ProfileBatch=serde_json::from_value(v.clone()).unwrap();
    assert_eq!(p.schema,"c3x-context-profile-batch-v1");assert_eq!(p.scientific_stage,STAGE);(v,p)
}
fn scope_command(discovery_path:PathBuf,profiles_path:PathBuf,out:PathBuf){
    let d=read_json(&discovery_path);assert_eq!(d["schema"],"c3x-field-discovery-v1");assert_eq!(d["scientific_stage"],STAGE);
    let (pv,p)=read_profiles(&profiles_path);
    let bases=d["minimal_portable_bases"].as_array().unwrap();
    if bases.is_empty(){
        let z=json!({"schema":"c3x-field-scope-v1","scientific_stage":STAGE,"status":"NO_DISCOVERY_BASIS",
            "discovery_sha256":sha_value(&d),"profiles_sha256":sha_value(&pv),"target_fields_consulted":false,
            "selected_basis_id":Value::Null,"predictions":[]});
        write_json(&out,&z);return;
    }
    let mut scored=Vec::new();
    for b in bases{
        let (seen,eng,pos,pospred,_)=scope_eval(b,&p.records);
        scored.push((seen,eng.len(),pos.len(),b["basis_id"].as_str().unwrap().to_string(),pospred));
    }
    scored.sort_by(|a,b|b.0.cmp(&a.0).then(b.1.cmp(&a.1)).then(b.2.cmp(&a.2)).then(a.3.cmp(&b.3)));
    let best=&scored[0];let basis=basis_lookup(&d,&best.3);
    let (seen,engines,positions,pospred,preds)=scope_eval(basis,&p.records);
    let n=p.records.len();let frac=if n==0{0.0}else{seen as f64/n as f64};
    let g=&d["heldout_scope_gate"];
    let min_frac=g["min_seen_fraction"].as_f64().unwrap();
    let req_eng=g["required_engines"].as_u64().unwrap() as usize;
    let min_posn=g["min_positions"].as_u64().unwrap() as usize;
    let min_pp=g["min_discovery_predicted_positive_profiles"].as_u64().unwrap() as usize;
    let pass=frac+1e-12>=min_frac&&engines.len()>=req_eng&&positions.len()>=min_posn&&pospred>=min_pp;
    let z=json!({
        "schema":"c3x-field-scope-v1","scientific_stage":STAGE,
        "status":if pass{"HELDOUT_SCOPE_SEALED"}else{"HOLDOUT_SCOPE_INSUFFICIENT"},
        "discovery_sha256":sha_value(&d),"profiles_sha256":sha_value(&pv),"target_fields_consulted":false,
        "selected_basis_id":best.3,"selected_coordinates":basis["coordinates"],
        "coverage":{"profiles":n,"seen":seen,"seen_fraction":frac,"covered_engines":engines,"covered_positions":positions,
            "discovery_predicted_positive_profiles":pospred,"gate_pass":pass},
        "predictions":preds,
        "selection_rule":"maximize seen profiles, then covered engines, then covered positions, then lexical basis ID; no held-out targets consulted"
    });
    write_json(&out,&z);
    println!("C3X_FIELD_SCOPE {} basis {} seen {}/{}",z["status"],best.3,seen,n);
}
fn query_command(discovery_path:PathBuf,bid:String,profiles_path:PathBuf,out:PathBuf){
    let d=read_json(&discovery_path);let (_pv,p)=read_profiles(&profiles_path);let b=basis_lookup(&d,&bid);
    let (seen,eng,pos,pospred,preds)=scope_eval(b,&p.records);
    let z=json!({"schema":"c3x-field-query-v1","scientific_stage":STAGE,"basis_id":bid,"coordinates":b["coordinates"],
        "profiles":p.records.len(),"seen":seen,"covered_engines":eng,"covered_positions":pos,
        "predicted_positive_profiles":pospred,"predictions":preds,"target_fields_consulted":false});
    write_json(&out,&z);
}
fn verify_command(scope_path:PathBuf,targets_path:PathBuf,out:PathBuf){
    let s=read_json(&scope_path);assert_eq!(s["schema"],"c3x-field-scope-v1");assert_eq!(s["scientific_stage"],STAGE);
    assert_eq!(s["target_fields_consulted"],false);
    let tv=read_json(&targets_path);let t:TargetBatch=serde_json::from_value(tv.clone()).unwrap();
    assert_eq!(t.schema,"c3x-context-target-batch-v1");assert_eq!(t.scientific_stage,STAGE);
    let tm:BTreeMap<String,&TargetRecord>=t.records.iter().map(|r|(r.record_id.clone(),r)).collect();
    let mut contradictions=Vec::new();let mut verified=0;let mut abstained=0;
    let mut cell_labels:BTreeMap<String,BTreeSet<bool>>=BTreeMap::new();
    for p in s["predictions"].as_array().unwrap(){
        let id=p["record_id"].as_str().unwrap();
        let tr=tm.get(id).unwrap_or_else(||panic!("missing target {id}"));
        let status=p["status"].as_str().unwrap();
        if status=="ABSTAIN_UNSEEN_CONTEXT"{abstained+=1;continue;}
        let pred=p["predicted_root_change"].as_bool().unwrap();verified+=1;
        let key=p["cell_key"].as_str().unwrap().to_string();cell_labels.entry(key).or_default().insert(tr.root_change);
        if pred!=tr.root_change{
            contradictions.push(json!({"record_id":id,"cell_key":p["cell_key"],"predicted_root_change":pred,
                "observed_root_change":tr.root_change,"parent_bestmove":tr.parent_bestmove,"counterfactual_bestmove":tr.counterfactual_bestmove}));
        }
    }
    let mixed:Vec<Value>=cell_labels.iter().filter(|(_,v)|v.len()>1).map(|(k,v)|json!({"cell_key":k,"labels":v})).collect();
    let gate=s["coverage"]["gate_pass"].as_bool().unwrap_or(false);
    let verdict=if !gate{"HOLDOUT_SCOPE_INSUFFICIENT"}else if !contradictions.is_empty()||!mixed.is_empty(){"CONTEXT_FIELD_TRANSPORT_FALSIFIED"}else{"CONTEXT_FIELD_TRANSPORT_CERTIFIED"};
    let z=json!({"schema":"c3x-field-verification-v1","scientific_stage":STAGE,"verdict":verdict,
        "scope_sha256":sha_value(&s),"targets_sha256":sha_value(&tv),"selected_basis_id":s["selected_basis_id"],
        "scope_gate_pass":gate,"covered_verified":verified,"abstained":abstained,
        "contradictions":contradictions,"mixed_heldout_cells":mixed,
        "authority_ceiling":"Certification applies only to covered held-out cells under the frozen field; unseen cells remain abstentions."});
    write_json(&out,&z);
    println!("C3X_FIELD_VERIFY {} verified {} abstained {}",verdict,verified,abstained);
}

fn main(){
    let cli=Cli::parse();
    match cli.command{
        Command::Discover{constitution,input,out}=>discovery_command(constitution,input,out),
        Command::Scope{discovery,profiles,out}=>scope_command(discovery,profiles,out),
        Command::Verify{scope,targets,out}=>verify_command(scope,targets,out),
        Command::Query{discovery,basis,profiles,out}=>query_command(discovery,basis,profiles,out),
    }
}

#[cfg(test)]
mod tests{
    use super::*;
    fn r(id:&str,engine:&str,pos:&str,x:&str,y:bool)->DiscoveryRecord{
        let mut c=BTreeMap::new();c.insert("x".into(),x.into());
        DiscoveryRecord{record_id:id.into(),engine:engine.into(),position_id:pos.into(),event_id:id.into(),
            fiber_id:"F0|A".into(),context:c,architecture_context:BTreeMap::new(),target:y}
    }
    #[test]fn context_splits_collision(){
        let rs=vec![r("1","a","p1","u",true),r("2","b","p2","v",false)];
        assert_eq!(metrics(&rs,&[]).collisions,1);
        assert_eq!(metrics(&rs,&["x".into()]).collisions,0);
    }
    #[test]fn combinations_count(){let x=vec!["a".into(),"b".into(),"c".into()];assert_eq!(combinations(&x,2).len(),3);}
}
