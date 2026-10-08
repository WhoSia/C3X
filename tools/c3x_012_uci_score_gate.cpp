#include <iostream>
#include <sstream>
#include <string>
#include <map>
#include <stdexcept>
using namespace std;
struct Record {int depth=0,cp=0;string move;bool valid=false;};
int main(int argc,char**argv){
 if(argc!=3){cerr<<"USAGE: gate MOVE_A MOVE_B\n";return 2;}
 const string a=argv[1],b=argv[2];
 if(a==b||a.size()<4||a.size()>5||b.size()<4||b.size()>5){cerr<<"INVALID_MOVES\n";return 2;}
 map<int,Record> scores;string line,best;
 try {
  while(getline(cin,line)){
   istringstream ss(line);string token;ss>>token;
   if(token=="bestmove"){ss>>best;continue;}
   if(token!="info")continue;
   int depth=-1,idx=-1,cp=0;bool hasScore=false,hasPv=false,bounded=false,mate=false;string move;
   while(ss>>token){
    if(token=="depth"){if(!(ss>>depth))throw runtime_error("BAD_DEPTH");}
    else if(token=="multipv"){if(!(ss>>idx))throw runtime_error("BAD_INDEX");}
    else if(token=="score"){
     string kind;ss>>kind;
     if(kind=="mate"){mate=true;int m;ss>>m;}
     else if(kind=="cp"){if(!(ss>>cp))throw runtime_error("BAD_CP");hasScore=true;}
     else throw runtime_error("UNKNOWN_SCORE");
    }else if(token=="lowerbound"||token=="upperbound")bounded=true;
    else if(token=="pv"){if(!(ss>>move))throw runtime_error("EMPTY_PV");hasPv=true;break;}
   }
   if(idx<1||idx>2||depth<0||!hasPv)continue;
   if(mate||bounded){scores.erase(idx);continue;}
   if(!hasScore)continue;
   if((move==a||move==b)){
     auto &r=scores[idx];if(depth>=r.depth)r={depth,cp,move,true};
   }
  }
  if(best!=a&&best!=b)throw runtime_error("BESTMOVE_OUTSIDE_PAIR");
  if(!scores[1].valid||!scores[2].valid)throw runtime_error("INCOMPLETE_MULTIPV");
  if(scores[1].depth!=scores[2].depth)throw runtime_error("MISMATCHED_DEPTH");
  if(scores[1].move==scores[2].move)throw runtime_error("DUPLICATE_PV_MOVE");
  int ca=scores[1].move==a?scores[1].cp:scores[2].cp;
  int cb=scores[1].move==b?scores[1].cp:scores[2].cp;
  cout<<"{\"status\":\"SYNTACTICALLY_COMPARABLE_CP_ONLY\",\"depth\":"<<scores[1].depth<<",\"move_a\":\""<<a<<"\",\"move_b\":\""<<b<<"\",\"cp_a\":"<<ca<<",\"cp_b\":"<<cb<<",\"delta_cp\":"<<(ca-cb)<<",\"legality_verified\":false,\"engine_identity_verified\":false,\"scientific_evidence\":false}\n";
  return 0;
 }catch(const exception&e){cerr<<"COMPARABILITY_HOLD:"<<e.what()<<"\n";return 3;}
}
