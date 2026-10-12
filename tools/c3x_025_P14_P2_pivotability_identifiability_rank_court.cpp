// C3X 0.25 P14-P2: abstract causal identification and exact rank-safety court.
// This is not an original Stockfish engine observation or a new mathematics theorem.
#include <array>
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <limits>
using Scores=std::array<int,3>;
void check(bool p,const char* reason){if(!p)throw std::runtime_error(reason);}
int winning_index(const Scores& s){
    return int(std::distance(s.begin(),std::max_element(s.begin(),s.end())));
}
int strict_margin(const Scores& s){
    int w=winning_index(s),m=std::numeric_limits<int>::max();
    for(int i=0;i<3;++i)if(i!=w)m=std::min(m,s[w]-s[i]);
    return m;
}
int sup_drift(const Scores& s,const Scores& t){
    int e=0;for(int i=0;i<3;++i)e=std::max(e,std::abs(s[i]-t[i]));
    return e;
}
struct PublicTrace {
    std::array<int,2> sampled_qsource{};
    int sampled_length=0;
    Scores final_root_candidates{};
    int final_winner=0,nodes=0;
    bool operator==(const PublicTrace& y)const{
      return sampled_qsource==y.sampled_qsource&&sampled_length==y.sampled_length&&
         final_root_candidates==y.final_root_candidates&&
         final_winner==y.final_winner&&nodes==y.nodes;
    }
};
struct HiddenWorld{PublicTrace published;int provisional_challenger=0;};
HiddenWorld compute(bool intervene,bool compensated_transient){
    HiddenWorld x{};
    x.published.sampled_qsource={intervene?7:4,intervene?9:0};
    x.published.sampled_length=intervene?2:1;
    x.published.nodes=30+int(intervene);
    x.published.final_root_candidates={10,6,2};
    x.published.final_winner=winning_index(x.published.final_root_candidates);
    x.provisional_challenger=compensated_transient&&intervene?3:6;
    return x;
}
int main(){
    const auto a0=compute(false,false),a1=compute(true,false);
    const auto b0=compute(false,true),b1=compute(true,true);
    // Same externally recorded Q events, final scores, winner and node count
    // under each intervention. Yet internal candidate mediation differs.
    check(a0.published==b0.published&&a1.published==b1.published,
      "causal-world observational equivalence violated");
    check(a0.provisional_challenger==a1.provisional_challenger,
      "inert mediator control invalid");
    check(b0.provisional_challenger!=b1.provisional_challenger,
      "unobserved transient root candidate countermodel absent");
    check(a0.published.final_winner==a1.published.final_winner&&
      a0.published.nodes!=a1.published.nodes,
      "intervened search can preserve final choice while changing execution");
    int certificates=0,uncertified_flips=0,pairs=0;
    // Finite regression for theorem: identical comparable candidate set, exact
    // full-vector scores with sup error epsilon, unique gap >2epsilon.
    for(int a=0;a<5;++a)for(int b=0;b<5;++b)for(int c=0;c<5;++c){
      Scores s={a,b,c};const int gap=strict_margin(s);
      for(int x=0;x<5;++x)for(int y=0;y<5;++y)for(int z=0;z<5;++z){
        Scores t={x,y,z};const int eps=sup_drift(s,t);
        if(gap>2*eps){
          ++certificates;
          check(winning_index(s)==winning_index(t),
            "strict rank-margin sufficient condition refuted");
        }else if(gap>0&&winning_index(s)!=winning_index(t)){
          ++uncertified_flips;
        }
        ++pairs;
      }
    }
    check(pairs==15625&&certificates==261&&uncertified_flips==7500,
      "finite theorem witness/negative controls census drift");
    std::cout<<"C3X025_P14P2_THEORETICAL_COURT_PASS"
      <<" indistinguishable_hidden_causal_worlds=2"
      <<" score_pairs="<<pairs
      <<" strict_margin_certificate_pairs="<<certificates
      <<" uncertified_root_flips="<<uncertified_flips
      <<" original_SF16_rank_safety_certificate=HOLD"
      <<" natural_TT_SEE_mediation=HOLD\n";
}
