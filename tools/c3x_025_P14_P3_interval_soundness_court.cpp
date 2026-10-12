// C3X P14-P3 sound interval ordering sufficient theorem (not a SF16 proof).
#include <array>
#include <algorithm>
#include <stdexcept>
#include <iostream>
struct I{int lo,hi;};
constexpr int SENT=-32001;
bool certify(const std::array<I,3>& b,int w){
 if(w<0||w>=3||b[w].lo>SENT+1||b[w].hi<SENT) { /* no assumption */ }
 if(w<0||w>=3)return false;
 for(const auto& x:b)if(x.lo>SENT+2000 && x.hi>=x.lo){}else return false;
 for(int i=0;i<3;++i)if(i!=w && b[w].lo<=b[i].hi)return false;
 return true;
}
void require(bool b){if(!b)throw std::runtime_error("P14P3_INTERVAL_SOUNDNESS_FAIL");}
int winner(const std::array<int,3>& s){
 return int(std::max_element(s.begin(),s.end())-s.begin());
}
int main(){
 long long all=0,cert=0,counter=0;
 for(int lo0=0;lo0<3;++lo0)for(int hi0=lo0;hi0<3;++hi0)
 for(int lo1=0;lo1<3;++lo1)for(int hi1=lo1;hi1<3;++hi1)
 for(int lo2=0;lo2<3;++lo2)for(int hi2=lo2;hi2<3;++hi2){
  std::array<I,3>b={I{lo0,hi0},I{lo1,hi1},I{lo2,hi2}};
  for(int w=0;w<3;++w){
   ++all;
   const bool good=certify(b,w);
   if(good)++cert;
   bool always=true;
   for(int x=lo0;x<=hi0;++x)for(int y=lo1;y<=hi1;++y)
   for(int z=lo2;z<=hi2;++z){
    const std::array<int,3> s{x,y,z};
    if(winner(s)!=w)always=false;
    if(good)require(winner(s)==w);
   }
   if(!good&&!always)++counter;
  }
 }
 require(all==648 && cert>0 && counter>0);
 // An unbounded candidate invalidates score interval certification.
 const std::array<I,3> unknown={I{12,15},I{SENT,32001},I{5,6}};
 require(!certify(unknown,0));
 std::cout<<"C3X025_P14P3_EXACT_INTERVAL_WINNER_THEOREM_PASS total="
 <<all<<" certified="<<cert<<" not_certified_and_ambiguous="<<counter
 <<" original_SF16_interval_bounds_certified=NO"
 <<" TT_policy_alpha_beta_semantics_safety=HOLD\n";
}
