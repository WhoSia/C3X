// P14-P6: CEGAR rival-directed refinement for finite JOINT candidate worlds.
// Trusted gap queries are a TOY oracle. Stockfish supplies no such proven oracle.
#[derive(Clone,Copy)]
struct W([i32;3]);
fn worlds()->Vec<W>{let mut x=Vec::new();for a in 0..3{for b in 0..3{for c in 0..3{x.push(W([a,b,c]));}}}x}
fn strict(k:&[W],w:usize)->bool{k.iter().all(|v|(0..3).filter(|r|*r!=w).all(|r|v.0[w]>v.0[r]))}
#[derive(Clone,Copy,PartialEq,Eq)]
enum ResultKind{Certified,Counterexample,Abstain}
fn cegar(k:&[W],w:usize,semantic_oracle:bool)->(ResultKind,usize){
 if !semantic_oracle {return (ResultKind::Abstain,0);}
 let mut upper=[2i32;3];upper[w]=-3;let mut rounds=0usize;
 loop{
  let next=(0..3).filter(|r|*r!=w&&upper[*r]>=0)
     .max_by_key(|r|(upper[*r],-(*r as i32)));
  let Some(r)=next else{return(ResultKind::Certified,rounds)};
  // Exact gap oracle models separately verified source-semantic re-search.
  // It is NOT available for actual Stockfish in P14-P6.
  let gap=k.iter().map(|v|v.0[r]-v.0[w]).max().unwrap();
  upper[r]=gap;rounds+=1;
  if gap>=0 {
    assert!(k.iter().any(|v|v.0[r]>=v.0[w]));
    return(ResultKind::Counterexample,rounds);
  }
  assert!(rounds<=2);
 }
}
fn main(){
 let all=worlds();assert_eq!(all.len(),27);
 let mut sets=0usize;let mut cert=0usize;let mut counter=0usize;
 let mut abstain=0usize;let mut queries=0usize;
 for i in 0..27{
  let single=[all[i]];run(&single,&mut sets,&mut cert,&mut counter,&mut abstain,&mut queries);
  for j in i+1..27 {
   let pair=[all[i],all[j]];run(&pair,&mut sets,&mut cert,&mut counter,&mut abstain,&mut queries);
   for k in j+1..27 {
    let triple=[all[i],all[j],all[k]];
    run(&triple,&mut sets,&mut cert,&mut counter,&mut abstain,&mut queries);
   }
  }
 }
 assert_eq!(sets,3303);
 assert_eq!(cert+counter,sets*3);
 assert_eq!(abstain,sets*3);
 println!("C3X025_P14P6_CEGAR_RIVAL_DIRECTED_TOY_PROOF_PASS worldsets={} strict_winner_certs={} real_counterexamples={} source_unproved_abstentions={} trusted_queries={} SF16_semantic_oracle=UNAVAILABLE Elo=UNTESTED",
  sets,cert,counter,abstain,queries);
}
fn run(k:&[W],sets:&mut usize,cert:&mut usize,counter:&mut usize,abstain:&mut usize,queries:&mut usize){
 *sets+=1;
 for w in 0..3{
  let (r,n)=cegar(k,w,true);
  *queries+=n;
  if strict(k,w){assert!(r==ResultKind::Certified);*cert+=1;}
  else{assert!(r==ResultKind::Counterexample);*counter+=1;}
  let (x,n)=cegar(k,w,false);
  assert!(x==ResultKind::Abstain&&n==0);
  *abstain+=1;
 }
}
