// C3X P14-P7: Stockfish16 source identity countermodel and conditional
// finite negamax/root interval theorem. NO original minimax-score proof.
#include <array>
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
using namespace std;
static void req(bool b,const char* m){if(!b)throw runtime_error(m);}
constexpr int INF=100000;
struct B{int l,u;};
B neg(B x){return {-x.u,-x.l};}
B mx(B a,B b){return {max(a.l,b.l),max(a.u,b.u)};}
B fromTT(int value,int beta,int flags,bool pv=false,bool depthOK=true,bool valid=true){
 const bool original=!pv&&depthOK&&valid&&(flags&(value>=beta?2:1));
 if(!original)return {-INF,INF};
 // An accepted original TT source return is NOT a mathematical assertion
 // about a true chess utility unless its writer/semantic contract is proven.
 return {-INF,INF};
}
bool alias(uint64_t a,uint64_t b){
 // Official Stockfish16 16 MiB: clusterCount=16*2^20/32=2^19.
 // mul_hi64(k,2^19) = high 19 key bits; stored key16 = low 16 bits.
 return (a>>45)==(b>>45)&&uint16_t(a)==uint16_t(b);
}
int main(){
 const uint64_t key=UINT64_C(0x135790000000ABCD);
 int distinctAliases=0;
 for(int m=1;m<=1023;m++){
  const uint64_t other=key^(uint64_t(m)<<16);
  req(other!=key&&alias(key,other),"short TT key/index collision witness invalid");
  distinctAliases++;
 }
 int hiddenScoreCounterworlds=0;
 for(int hidden=-3;hidden<=3;hidden++){
  const B x=fromTT(-2,0,1); // original UPPER-tag source branch accepted
  req(x.l==-INF&&x.u==INF,"source TT branch faked true score bound");
  hiddenScoreCounterworlds+=int(hidden>-2);
 }
 req(hiddenScoreCounterworlds>0,"semantic nonidentifiability missing");
 int worlds=0,negamaxChecks=0,windowChecks=0,safeLower=0,safeUpper=0;
 for(int a=-3;a<=3;a++)for(int b=-3;b<=3;b++)for(int c=-3;c<=3;c++){
  worlds++;
  array<int,3> child{a,b,c};
  array<B,3> move{};
  for(int k=0;k<3;k++){
   const B trusted{child[k]-1,child[k]+1}; // ASSUMED sound
   move[k]=neg(trusted);
   const int actual=-child[k];
   req(move[k].l<=actual&&actual<=move[k].u,"negamax interval unsound");
   negamaxChecks++;
  }
  const B parent=mx(mx(move[0],move[1]),move[2]);
  const int exact=max({-a,-b,-c});
  req(parent.l<=exact&&exact<=parent.u,"sibling max interval unsound");
  negamaxChecks++;
  for(int k=0;k<3;k++)for(int beta=-3;beta<=3;beta++){
   const int actual=-child[k];
   if(move[k].l>=beta){req(actual>=beta,"sound lower interval broken");safeLower++;}
   if(move[k].u<beta){req(actual<beta,"sound upper interval broken");safeUpper++;}
   windowChecks++;
  }
 }
 req(worlds==343&&distinctAliases==1023,"abstract corpus size changed");
 // Equal stored score is NOT a uniquely selected chess move:
 // original RootMove uses previousScore and stable input order.
 struct Root{int score,previous;};
 Root x{2,1},y{2,2};
 req(x.score==y.score&&y.previous>x.previous,"tie counterexample invalid");
 cout<<"C3X025_P14P7_COMPOSITIONAL_SEARCH_CONTRACT_PASS"
  <<" distinct_abstract_shortkey_aliases="<<distinctAliases
  <<" abstract_hidden_score_counterworlds="<<hiddenScoreCounterworlds
  <<" finite_3child_worlds="<<worlds
  <<" sound_assumed_semantic_interval_checks="<<negamaxChecks
  <<" window_checks="<<windowChecks
  <<" conditional_lower_lifts="<<safeLower
  <<" conditional_upper_lifts="<<safeUpper
  <<" original_TT_tag_true_value=UNPROVEN full_SF16_K=HOLD Elo=UNTESTED\n";
}
