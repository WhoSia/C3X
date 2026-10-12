// C3X P14-P8: bilateral evidence under/over reachable-world approximations.
// Mathematical finite model, NOT an original Stockfish world oracle.
#include <iostream>
#include <stdexcept>
using namespace std;
constexpr int N=5, FULL=(1<<N)-1;
constexpr int chosen[N]={0,1,2,0,1};
void check(bool v,const char* msg){if(!v)throw runtime_error(msg);}
bool possible(int set,int w){
  for(int i=0;i<N;i++)if((set>>i&1)&&chosen[i]==w)return true;
  return false;
}
bool necessary(int set,int w){
  for(int i=0;i<N;i++)if((set>>i&1)&&chosen[i]!=w)return false;
  return true;
}
int main(){
 int triplets=0,queries=0,yes=0,no=0,forced=0,refuted=0;
 int fakePositiveFromOuter=0,fakeForcedFromInner=0;
 for(int inner=0;inner<=FULL;inner++)
 for(int actual=1;actual<=FULL;actual++)
 for(int outer=0;outer<=FULL;outer++){
   if((inner&~actual)||(actual&~outer))continue;
   triplets++;
   for(int w=0;w<3;w++){
     queries++;
     bool p=possible(actual,w),n=necessary(actual,w);
     if(possible(inner,w)){check(p,"inner witness was unreachable");yes++;}
     if(!possible(outer,w)){check(!p,"outer absence excluded real possibility");no++;}
     if(necessary(outer,w)){check(n,"outer universal claim false");forced++;}
     bool badWitness=false;
     for(int i=0;i<N;i++)if((inner>>i&1)&&chosen[i]!=w)badWitness=true;
     if(badWitness){check(!n,"real rival witness did not refute necessity");refuted++;}
     fakePositiveFromOuter+=int(possible(outer,w)&&!p);
     fakeForcedFromInner+=int(necessary(inner,w)&&!n);
   }
 }
 check(triplets==992,"nonempty sandwich enumeration mismatch");
 check(fakePositiveFromOuter>0&&fakeForcedFromInner>0,"invalid inferences had no countermodels");
 cout<<"C3X025_P14P8_BILATERAL_WARRANT_FINITE_PASS"
  <<" reachable_set_triplets="<<triplets<<" queries="<<queries
  <<" under_real_possibility="<<yes<<" over_impossibility="<<no
  <<" over_necessary="<<forced<<" under_refuted_necessity="<<refuted
  <<" fake_possibilities_from_outer="<<fakePositiveFromOuter
  <<" fake_necessities_from_inner="<<fakeForcedFromInner
  <<" actual_Stockfish_K=UNPROVEN Elo=UNTESTED\n";
}
