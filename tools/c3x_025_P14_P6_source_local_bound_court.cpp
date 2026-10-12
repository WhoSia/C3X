// Source-exact Stockfish16 qsearch TT early-return branch certificate.
// This proves only original CONTROL FLOW conditions, NOT minimax/root score.
#include <iostream>
#include <stdexcept>
#include <cstdint>
enum Bound{NONE=0,UPPER=1,LOWER=2,EXACT=3};
struct S {bool pv,hit,valid;int stored_depth,required_depth,bound,value,beta;};
bool actual(S x){return !x.pv && x.stored_depth>=x.required_depth && x.valid &&
  (x.bound & (x.value>=x.beta?LOWER:UPPER));}
bool local_cert(S x,bool lower){
  if(!actual(x))return false;
  return lower ? x.value>=x.beta && (x.bound&LOWER)!=0
               : x.value<x.beta && (x.bound&UPPER)!=0;
}
void req(bool b,const char* msg){if(!b)throw std::runtime_error(msg);}
int main(){
 long long states=0,accepted=0,lower=0,upper=0;
 long long naive_value_false=0,false_if_only_bound=0;
 for(int pv=0;pv<2;pv++)for(int hit=0;hit<2;hit++)
 for(int valid=0;valid<2;valid++)for(int depth=-1;depth<=2;depth++)
 for(int reqDepth=0;reqDepth<=2;reqDepth++)for(int bound=0;bound<=3;bound++)
 for(int v=-2;v<=2;v++)for(int beta=-2;beta<=2;beta++){
   S x{bool(pv),bool(hit),bool(valid&&hit),depth,reqDepth,bound,v,beta};
   states++;
   const bool acceptedSite=actual(x);
   const bool cLower=local_cert(x,true),cUpper=local_cert(x,false);
   req((cLower||cUpper)==acceptedSite,"site predicate not certificate-complete");
   req(!(cLower&&cUpper),"exclusive comparison sides violated");
   req(!cLower||(!x.pv&&x.valid&&x.stored_depth>=x.required_depth&&x.value>=x.beta),"lower cut unsound");
   req(!cUpper||(!x.pv&&x.valid&&x.stored_depth>=x.required_depth&&x.value<x.beta),"upper cut unsound");
   accepted+=acceptedSite;lower+=cLower;upper+=cUpper;
   const bool naiveTag=(bound&LOWER) && (v>=beta);
   false_if_only_bound += bool(naiveTag&&!acceptedSite);
   // Counterexample: the same accepted TT fields can coexist in the
   // ABSTRACT state family with unknown true target move utilities either
   // way. The source code supplies no theorem connecting such utilities.
   if(acceptedSite)for(int hidden=-3;hidden<=3;hidden++)
     naive_value_false+= ((v>=beta)!=(hidden>=beta));
 }
 req(accepted==lower+upper && lower>0&&upper>0,"real both bound classes absent");
 req(naive_value_false>0&&false_if_only_bound>0,"unsound generalization counterexample absent");
 std::cout<<"C3X025_P14P6_SOURCE_CUTOFF_LOCAL_BRANCH_CERTIFICATE_PASS"
  <<" states="<<states<<" accepted="<<accepted
  <<" lower="<<lower<<" upper="<<upper
  <<" insufficient_bound_tags="<<false_if_only_bound
  <<" hidden_value_counterworlds="<<naive_value_false
  <<" source_local_predicate_sound=TRUE"
  <<" actual_true_chess_score_semantics=UNPROVEN"
  <<" root_contender_gap=UNPROVEN Elo=UNTESTED\n";
}
