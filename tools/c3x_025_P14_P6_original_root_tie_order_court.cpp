// P14-P6: original Stockfish16 RootMove::operator< + stable_sort
// exact OPERATIONAL ordering certificate. Not a minimax/game truth certificate.
#include <algorithm>
#include <array>
#include <iostream>
#include <stdexcept>
using namespace std;
struct Root {int id,score,previous,originalIndex;};
bool sourceLess(const Root& self,const Root& other) {
 return other.score!=self.score ? other.score<self.score
                                 : other.previous<self.previous;
}
void require(bool x,const char* m){if(!x)throw runtime_error(m);}
int main(){
 int inputSets=0,total=0,firstScoreTie=0,exactScorePreviousTie=0;
 array<int,3> p{0,1,2};
 for(int a=0;a<9;a++)for(int b=0;b<9;b++)for(int c=0;c<9;c++){
  array<int,3> v{a,b,c};inputSets++;
  p={0,1,2};
  do {
   array<Root,3> x{};
   for(int i=0;i<3;i++)x[i]={p[i],v[p[i]]/3-1,v[p[i]]%3-1,i};
   auto y=x;
   stable_sort(y.begin(),y.end(),sourceLess);
   for(int i=0;i<3;i++)for(int j=i+1;j<3;j++){
    const auto& l=y[i];const auto& r=y[j];
    require(l.score>r.score||
       (l.score==r.score&&l.previous>=r.previous),
       "original RootMove comparator order unsound");
    if(l.score==r.score&&l.previous==r.previous)
      require(l.originalIndex<r.originalIndex,"original stable tie order changed");
   }
   auto z=x;
   sort(z.begin(),z.end(),[](const Root& l,const Root& r){
    return l.score!=r.score?l.score>r.score:
           l.previous!=r.previous?l.previous>r.previous:
           l.originalIndex<r.originalIndex;
   });
   for(int i=0;i<3;i++)require(y[i].id==z[i].id,"lexicographic source abstraction failed");
   firstScoreTie+=int(y[0].score==y[1].score);
   exactScorePreviousTie+=int(y[0].score==y[1].score&&
                              y[0].previous==y[1].previous);
   total++;
  }while(next_permutation(p.begin(),p.end()));
 }
 require(inputSets==729&&total==4374&&firstScoreTie>0&&exactScorePreviousTie>0,
    "finite source lexical tie test census drift");
 cout<<"C3X025_P14P6_ORIGINAL_ROOT_STABLE_LEXICOGRAPHIC_ORDER_PASS"
  <<" candidate_multisets="<<inputSets<<" input_permutations="<<total
  <<" top_score_ties="<<firstScoreTie<<" exact_top_tuple_ties="<<exactScorePreviousTie
  <<" source_local_order_certificate=TRUE"
  <<" game_theoretic_winner_certificate=HOLD Elo=UNTESTED\n";
}
