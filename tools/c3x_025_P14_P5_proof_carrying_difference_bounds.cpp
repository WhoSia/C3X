// P14-P5: proof-carrying difference bounds over JOINT candidate values.
// Toy candidate utilities only; actual Stockfish score soundness NOT assumed.
// Directed edge i->j c means v[j]-v[i] <= c. Floyd-Warshall closure is sound
// for these difference constraints; trace-only claims never enter certificates.
#include <array>
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
constexpr int N=4, INF=10000; // zero/reference, A, B, C
struct Edge { int i,j,c; };
struct Evidence { Edge e; bool proved_semantic_rule; };
struct DBM {
  array<array<int,N>,N> d{};
  DBM(){
    for(int i=0;i<N;i++)for(int j=0;j<N;j++)d[i][j]=i==j?0:INF;
    for(int i=1;i<N;i++){d[0][i]=3;d[i][0]=0;} // TOY [0,3], NOT SF16
  }
  void add(Edge e){d[e.i][e.j]=min(d[e.i][e.j],e.c);}
  bool addEvidence(Evidence e){
    if(!e.proved_semantic_rule)return false; // STRICT ABSTAIN
    add(e.e);return true;
  }
  bool close(){
    for(int k=0;k<N;k++)for(int i=0;i<N;i++)for(int j=0;j<N;j++)
      if(d[i][k]!=INF&&d[k][j]!=INF)
        d[i][j]=min(d[i][j],d[i][k]+d[k][j]);
    for(int i=0;i<N;i++)if(d[i][i]<0)return false;
    return true;
  }
  bool certA() const {return d[1][2]<=-1&&d[1][3]<=-1;}
  bool boxA() const {return -d[1][0]>max(d[0][2],d[0][3]);}
};
void need(bool x,const char* message){if(!x)throw runtime_error(message);}
bool holds(Edge e,const array<int,N>& v){return v[e.j]-v[e.i]<=e.c;}
int main(){
  vector<Edge> options;
  for(int i=1;i<N;i++)for(int j=1;j<N;j++)if(i!=j)
    for(int c=-3;c<=3;c++)options.push_back({i,j,c});
  need(options.size()==42,"invalid finite rule corpus");
  long long systems=0,consistent=0,dbmCert=0,intervalCert=0,relExtra=0;
  long long closureChecks=0,certChecks=0,nonCertAndCounterexample=0;
  // All 0, 1 or 2 difference-constraint systems over 3 moves (scores 0..3).
  for(size_t p=0;p<=options.size();p++)
    for(size_t q=p;q<=options.size();q++){
      vector<Edge> rules;
      if(p<options.size())rules.push_back(options[p]);
      if(q<options.size())rules.push_back(options[q]);
      systems++;
      DBM dbm;for(auto e:rules)dbm.add(e);
      const bool consistentClosure=dbm.close();
      int count=0;bool allStrictA=true;
      for(int a=0;a<=3;a++)for(int b=0;b<=3;b++)for(int c=0;c<=3;c++){
        array<int,N> v{0,a,b,c};
        bool feasible=true;for(auto e:rules)feasible &= holds(e,v);
        if(!feasible)continue;
        count++;allStrictA &= a>b&&a>c;
        for(int i=0;i<N;i++)for(int j=0;j<N;j++)
          if(dbm.d[i][j]!=INF){
            need(v[j]-v[i]<=dbm.d[i][j],"closure excluded actual possible world");
            closureChecks++;
          }
      }
      need(consistentClosure==(count>0),"DBM missed exact satisfiability in toy model");
      if(!consistentClosure)continue;
      consistent++;
      const bool r=dbm.certA(),b=dbm.boxA();
      dbmCert+=int(r);intervalCert+=int(b);
      need(!b||r,"interval certificate unsound");
      if(r){
        certChecks++;
        need(allStrictA,"RELATIONAL_CERTIFICATE_FALSE_POSITIVE");
      }
      relExtra+=int(r&&!b);
      nonCertAndCounterexample+=int(!r&&!allStrictA);
    }
  DBM chain;
  // A>B>C but marginal intervals touch, so only relational certificate succeeds.
  need(chain.addEvidence({{1,2,-1},true}),"edge1 not admitted");
  need(chain.addEvidence({{2,3,-1},true}),"edge2 not admitted");
  need(chain.close()&&chain.certA()&&!chain.boxA(),"genuinely relational witness absent");
  // One recorded execution can be consistent with mutually incompatible future
  // root winners in two otherwise observationally identical hidden worlds.
  const array<int,3> seen{2,1,0},unseen{0,2,1};
  const string traceA="root=A recorded qreturn=1",traceB="root=A recorded qreturn=1";
  need(traceA==traceB&&seen[0]>seen[1]&&unseen[0]<unseen[1],
       "trace-only identifiability countermodel absent");
  DBM provenanceGated;
  need(!provenanceGated.addEvidence({{1,2,-1},false}),"observational guess passed proof gate");
  need(!provenanceGated.addEvidence({{1,3,-1},false}),"observational guess passed proof gate");
  need(provenanceGated.close()&&!provenanceGated.certA(),
       "an empirical root trace forged a robust certificate");
  need(systems==946&&consistent>0&&dbmCert>intervalCert&&relExtra>0);
  cout<<"C3X025_P14P5_PROOF_CARRYING_DIFFERENCE_BOUNDS_PASS"
    <<" systems="<<systems<<" consistent="<<consistent
    <<" relational_cert="<<dbmCert<<" marginal_interval_cert="<<intervalCert
    <<" extra_relational="<<relExtra
    <<" closure_world_checks="<<closureChecks
    <<" certificate_checks="<<certChecks
    <<" noncert_counterexamples="<<nonCertAndCounterexample
    <<" empirical_only_constraints_admitted=0"
    <<" SF16_semantic_K=HOLD SF16_Elo=UNTESTED\n";
}
