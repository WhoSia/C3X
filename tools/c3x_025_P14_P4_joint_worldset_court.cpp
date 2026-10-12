// C3X 0.25-P14-P4. Finite mathematical court for information order on
// joint candidate-score worlds. NOT a Stockfish score certificate.
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>
constexpr int W=16; // two moves, scores 0..3 => 4x4 possible exact worlds
void need(bool x){if(!x)throw std::runtime_error("RELATIONAL_ORDER_FAILED");}
bool robust(std::uint32_t k){
 if(!k)return false; // the empty model is INCONSISTENT, not robust
 for(int i=0;i<W;++i)if(k&(1u<<i)){int a=i/4,b=i%4;if(a<=b)return false;}
 return true;
}
bool rectangular(std::uint32_t k){
 if(!k)return false;
 int la=4,ub=-1;
 for(int i=0;i<W;++i)if(k&(1u<<i)){int a=i/4,b=i%4;
  if(a<la)la=a;
  if(b>ub)ub=b;
 }
 return la>ub;
}
int main(){
 long long nonempty=0,rel=0,box=0,relNotBox=0,refines=0;
 for(std::uint32_t k=1;k<(1u<<W);++k){
  ++nonempty;
  const bool r=robust(k),b=rectangular(k);
  if(r)++rel;
  if(b)++box;
  need(!b||r);
  if(r&&!b)++relNotBox;
  for(int i=0;i<W;++i)if(k&(1u<<i)){
   std::uint32_t refined=k&~(1u<<i);
   if(refined){++refines;need(!r||robust(refined));}
  }
 }
 // Worlds (1,0) and (2,1), both strict winner a, yet marginal intervals
 // of a=[1,2] and b=[0,1] overlap at 1. Relation is essential.
 const auto correlated=(1u<<(1*4+0)) | (1u<<(2*4+1));
 need(robust(correlated)&&!rectangular(correlated));
 // Even one observed stable world cannot certify stability over two worlds.
 const auto mixed=correlated | (1u<<(0*4+2));
 need(!robust(mixed));
 need(nonempty==65535&&relNotBox>0&&refines>0);
 std::cout<<"C3X025_P14P4_JOINT_WORLDSET_INFORMATION_LATTICE_PASS"
  <<" models="<<nonempty<<" robust="<<rel<<" marginal_certified="<<box
  <<" relational_only_certified="<<relNotBox
  <<" refinement_edges_checked="<<refines
  <<" original_SF16_actual_root_score_joint_set_certified=HOLD\n";
}
