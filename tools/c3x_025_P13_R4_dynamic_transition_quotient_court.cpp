// C3X P13-R4 finite dynamic quotient countermodel (NOT Stockfish evidence).
#include <map>
#include <set>
#include <tuple>
#include <vector>
#include <iostream>
#include <stdexcept>
struct S {int board,history,writer,generation;};
using B=std::tuple<int,int>;
using BW=std::tuple<int,int,int>;
B pi(S x){return {x.board,x.history};}
BW enriched(S x){return {x.board,x.history,x.writer};}
int action(S x){return (x.board+x.history)%3;}
S transition(S x){return {x.board^x.writer,x.history,x.writer,x.generation^1};}
S sham(S x){return {x.board,x.history,x.writer,x.generation^1};}
void require(bool p,const char* why){if(!p)throw std::runtime_error(why);}
int main(){
 std::vector<S> states;
 for(int b=0;b!=2;++b)for(int h=0;h!=2;++h)
 for(int w=0;w!=2;++w)for(int g=0;g!=2;++g)
   states.push_back({b,h,w,g});
 std::map<B,std::set<int>> current_actions;
 std::map<B,std::set<B>> next_public,sham_public;
 std::map<BW,std::set<BW>> next_enriched;
 for(const auto x: states){
   current_actions[pi(x)].insert(action(x));
   next_public[pi(x)].insert(pi(transition(x)));
   sham_public[pi(x)].insert(pi(sham(x)));
   next_enriched[enriched(x)].insert(enriched(transition(x)));
 }
 std::size_t action_conflict=0,next_conflict=0,sham_conflict=0,enriched_conflict=0;
 for(const auto &e:current_actions)action_conflict+=e.second.size()>1;
 for(const auto &e:next_public)next_conflict+=e.second.size()>1;
 for(const auto &e:sham_public)sham_conflict+=e.second.size()>1;
 for(const auto &e:next_enriched)enriched_conflict+=e.second.size()>1;
 require(states.size()==16,"exhaustiveness");
 require(action_conflict==0,"action projection must factor");
 require(next_conflict==4,"transition should fail all four public fibers");
 require(sham_conflict==0,"sham transition must preserve public quotient");
 require(enriched_conflict==0,"one-bit writer enrichment should restore congruence");
 std::cout<<"C3X025_P13_R4_DYNAMIC_QUOTIENT_ABSTRACT_PASS states="<<states.size()
   <<" action_collision="<<action_conflict
   <<" future_transition_collision="<<next_conflict
   <<" sham_collision="<<sham_conflict
   <<" enriched_transition_collision="<<enriched_conflict
   <<" missing_writer_bit=1 native_engine_proof=NO\n";
}
