// P14-P5: robust-winner query needs sound PAIRWISE CHALLENGER extrema,
// not the full feasible K. Finite exact-world theorem court; not Stockfish K.
#[derive(Clone,Copy)]
struct World([i32;3]);
fn all_worlds()->Vec<World>{let mut v=Vec::new();for a in 0..3{for b in 0..3{for c in 0..3{v.push(World([a,b,c]));}}}v}
fn gap(k:&[World],w:usize,r:usize)->i32{k.iter().map(|v|v.0[r]-v.0[w]).max().unwrap()}
fn exact(k:&[World],w:usize)->bool{(0..3).filter(|r|*r!=w).all(|r|gap(k,w,r)<0)}
fn actual(k:&[World],w:usize)->bool{k.iter().all(|v|(0..3).filter(|r|*r!=w).all(|r|v.0[w]>v.0[r]))}
fn boxcert(k:&[World],w:usize)->bool{
 let lo=k.iter().map(|v|v.0[w]).min().unwrap();
 (0..3).filter(|r|*r!=w).all(|r|lo>k.iter().map(|v|v.0[r]).max().unwrap())
}
#[derive(Default)]
struct Stats{systems:usize,robust:usize,box_cert:usize,rel_extra:usize,abstain_sound_approx:usize,refinement_edges:usize}
fn test(k:&[World],s:&mut Stats){
 assert!(!k.is_empty());s.systems+=1;
 for w in 0..3{
  let r=actual(k,w);let t=exact(k,w);let b=boxcert(k,w);
  assert_eq!(r,t,"query-completeness requires exact challenger differences");
  assert!(!b||r,"unsound Cartesian interval");
  s.robust+=usize::from(r);s.box_cert+=usize::from(b);
  s.rel_extra+=usize::from(r&&!b);
  let conservative=(0..3).filter(|j|*j!=w).all(|j|gap(k,w,j)+1<0);
  assert!(!conservative||r,"one-sided sound gap overapprox must not forge winner");
  s.abstain_sound_approx+=usize::from(r&&!conservative);
  if k.len()>1{for skip in 0..k.len(){
   let sub:Vec<World>=k.iter().enumerate().filter_map(|(i,v)|if i==skip{None}else{Some(*v)}).collect();
   for j in 0..3{if j!=w{assert!(gap(&sub,w,j)<=gap(k,w,j));}}
   if r{assert!(actual(&sub,w));}
   s.refinement_edges+=1;
  }}
 }
}
fn main(){
 let worlds=all_worlds();assert_eq!(worlds.len(),27);
 let mut s=Stats::default();
 for i in 0..27{
  test(&worlds[i..i+1],&mut s);
  for j in i+1..27{
   test(&[worlds[i],worlds[j]],&mut s);
   for k in j+1..27{test(&[worlds[i],worlds[j],worlds[k]],&mut s);}
  }
 }
 assert_eq!(s.systems,3303);
 let witness=[World([1,0,0]),World([2,1,1])];
 assert!(exact(&witness,0)&&actual(&witness,0)&&!boxcert(&witness,0));
 assert!(s.rel_extra>0&&s.abstain_sound_approx>0);
 println!("C3X025_P14P5_TIGHT_CHALLENGER_GAP_QUERY_COMPLETE_PASS systems={} robust={} boxes={} relational_extra={} safe_approx_abstentions={} refinements={} SF16_semantic_bounds=HOLD ELO=UNTESTED",
 s.systems,s.robust,s.box_cert,s.rel_extra,s.abstain_sound_approx,s.refinement_edges);
}
