// Chess strength statistical protocol, synthetic test only; zero real games.
use std::collections::BTreeMap;
struct Pair<'a> {opening:&'a str,white:Option<f64>,black:Option<f64>}
struct Summary {n:usize,mean:f64,epsilon:f64,lower:f64,upper:f64}
fn audit(data:&str)->Result<Summary,String>{
 let mut seen:BTreeMap<&str,Pair<'_>>=BTreeMap::new();
 for (i,line) in data.lines().enumerate(){
  if i==0 && line=="pair_id,opening_id,candidate_color,points"{continue;}
  let x:Vec<_>=line.split(',').collect();
  if x.len()!=4||x.iter().any(|v|v.trim()!=*v||v.is_empty()){return Err("malformed row".into());}
  let p=x[3].parse::<f64>().map_err(|_|"invalid score")?;
  if !(p==0.0||p==0.5||p==1.0){return Err("not allowed WDL point".into());}
  let rec=seen.entry(x[0]).or_insert(Pair{opening:x[1],white:None,black:None});
  if rec.opening!=x[1]{return Err("opening mismatch".into());}
  let slot=match x[2]{"W"=>&mut rec.white,"B"=>&mut rec.black,_=>return Err("bad color".into())};
  if slot.replace(p).is_some(){return Err("duplicate color".into());}
 }
 if seen.is_empty(){return Err("no opening pairs".into());}
 let mut xs=Vec::new();
 for p in seen.values(){
  let (Some(w),Some(b))=(p.white,p.black) else{return Err("missing color".into());};
  xs.push((w+b)/2.0); // one score in [0,1] per color-swapped pair
 }
 let n=xs.len();let mean=xs.iter().sum::<f64>()/n as f64;
 // Two-sided Hoeffding 95% for INDEPENDENT opening pairs; no game-level iid.
 let epsilon=((40.0_f64).ln()/(2.0*n as f64)).sqrt();
 Ok(Summary{n,mean,epsilon,lower:(mean-epsilon).max(0.0),upper:(mean+epsilon).min(1.0)})
}
fn main(){
 let data="pair_id,opening_id,candidate_color,points\n1,kings-pawn,W,1\n1,kings-pawn,B,0.5\n2,queen-pawn,W,0\n2,queen-pawn,B,0.5\n3,english,W,0.5\n3,english,B,0.5\n4,reti,W,1\n4,reti,B,1\n";
 let s=audit(data).expect("synthetic balanced pairs");
 assert_eq!(s.n,4);
 assert!(s.lower<=s.mean&&s.mean<=s.upper&&s.epsilon>0.0);
 for bad in [
  data.replace("1,kings-pawn,B,0.5","1,kings-pawn,W,0.5"),
  data.replace("1,kings-pawn,B,0.5","1,italian,B,0.5"),
  data.replace("2,queen-pawn,B,0.5","2,queen-pawn,B,0.8"),
  data.replace("3,english,B,0.5\n","")
 ]{assert!(audit(&bad).is_err(),"broken paired trial accepted");}
 println!("C3X025_P14P7_STRENGTH_TRIAL_PROTOCOL_COURT_PASS synthetic_pairs={} invalid_fixture_rejected=4 pair_Hoeffding95_halfwidth={:.6} real_games=0 measured_Elo=UNTESTED",s.n,s.epsilon);
}
