// C3X 0.25-P13 — finite behavioral-quotient and lineage certificate court.
// This is a constructive C++ reference, NOT a measured Stockfish improvement.
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <tuple>
#include <vector>
struct State {int b,h,gen,writer;};
struct World {State s; int policy,action;};
struct Result {bool factors; int max_actions,contradictory_fibers,bits;};
template<class Projection> Result analyze(const std::vector<World>& w,int policy,Projection pi){
  std::map<decltype(pi(w.at(0).s)),std::set<int>> fibers;
  for(const auto& e:w)if(e.policy==policy)fibers[pi(e.s)].insert(e.action);
  if(fibers.empty())throw std::runtime_error("empty fixed policy");
  int conflicts=0,maxk=0;
  for(auto& item:fibers){int k=int(item.second.size());maxk=std::max(maxk,k);conflicts+=k>1;}
  int bits=0;for(int x=maxk-1;x>0;x>>=1)++bits;
  return {conflicts==0,maxk,conflicts,bits};
}
struct Event {enum Kind{WRITER,TT_RETURN,CALLER,ASSIGN,UPDATE,ROOT,FINAL} kind;
              int id,parent,score,root;bool executed;};
const Event* find(const std::vector<Event>& v,Event::Kind k){
  const Event* p=nullptr;
  for(const auto& e:v)if(e.kind==k&&e.executed){
    if(p)throw std::runtime_error("ambiguous event cannot be spliced");
    p=&e;
  }
  return p;
}
struct Cert{bool writer_return,parent_frame,assigned,decision,terminal,natural_SEE;};
Cert court(const std::vector<Event>& es){
  auto w=find(es,Event::WRITER),r=find(es,Event::TT_RETURN);
  auto p=find(es,Event::CALLER),a=find(es,Event::ASSIGN);
  auto d=find(es,Event::UPDATE),u=find(es,Event::ROOT),f=find(es,Event::FINAL);
  bool wr=w&&r&&r->parent==w->id;
  bool rp=wr&&p&&p->parent==r->id&&p->root==r->root;
  bool pa=rp&&a&&a->parent==p->id&&a->score==-r->score&&a->root==p->root;
  bool ad=pa&&d&&d->parent==a->id&&d->score==a->score;
  bool end=ad&&u&&f&&u->parent==d->id&&f->parent==u->id&&f->root==r->root;
  // A fully witnessed observational dataflow is not a natural indirect effect.
  return {wr,rp,pa,ad,end,false};
}
void check(bool p,const char* why){if(!p)throw std::runtime_error(why);}
int main(){
  std::vector<World> v;
  for(int b=0;b!=2;++b)for(int h=0;h!=2;++h)
  for(int gen=0;gen!=2;++gen)for(int writer=0;writer!=2;++writer)
  for(int policy=0;policy!=2;++policy){
    State s{b,h,gen,writer};
    int a=policy==0?(b+h+writer)%3:(b+h)%3;
    v.push_back({s,policy,a});
  }
  auto board=[](State s){return std::make_tuple(s.b,s.h);};
  auto whole=[](State s){return std::make_tuple(s.b,s.h,s.gen,s.writer);};
  auto fixed=analyze(v,0,board),full=analyze(v,0,whole),control=analyze(v,1,board);
  check(v.size()==32&&!fixed.factors&&fixed.max_actions==2
    &&fixed.contradictory_fibers==4&&fixed.bits==1,"fiber theorem witness");
  check(full.factors&&control.factors,"fixed-policy negative control");
  std::vector<Event> trace={
    {Event::WRITER,1,0,30,10,true},
    {Event::TT_RETURN,2,1,30,10,true},
    {Event::CALLER,3,2,30,10,true}};
  auto p12=court(trace);
  check(p12.parent_frame&&!p12.assigned&&!p12.natural_SEE,"P12 boundary");
  trace.push_back({Event::ASSIGN,4,3,-30,10,true});
  auto p13=court(trace);
  check(p13.assigned&&!p13.decision,"parent assignment is not root impact");
  trace.push_back({Event::UPDATE,5,4,-30,10,true});
  trace.push_back({Event::ROOT,6,5,-30,10,true});
  trace.push_back({Event::FINAL,7,6,1,10,true});
  auto completed=court(trace);
  check(completed.terminal&&!completed.natural_SEE,"false mediator promotion");
  trace[3].score=-29;
  check(!court(trace).assigned,"invalid negamax sign accepted");
  trace[3].score=-30;trace[3].parent=99;
  check(!court(trace).assigned,"fabricated parent accepted");
  std::cout<<"C3X025_P13_CPP_ABSTRACT_PASS states="<<v.size()
           <<" contradictory_fibers="<<fixed.contradictory_fibers
           <<" extra_bits="<<fixed.bits
           <<" P13_NATIVE=HOLD P14_NATURAL_SEE=HOLD P15_STRENGTH=UNMEASURED\n";
}
