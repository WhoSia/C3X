#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;constexpr int P=9;constexpr double TH=0.50;
struct R{string sha,fam,side,sq;array<double,P> z{};long long tt=0,pq=0;};
vector<string> split(const string&s,char d){vector<string>v;stringstream ss(s);string x;while(getline(ss,x,d))v.push_back(x);return v;}
double var(const vector<double>&x){if(x.size()<2)return 0;double m=0;for(double v:x)m+=v;m/=x.size();double s=0;for(double v:x)s+=(v-m)*(v-m);return s/(x.size()-1);}
double smd(const vector<double>&a,const vector<double>&b){double ma=0,mb=0;for(double x:a)ma+=x;for(double x:b)mb+=x;ma/=a.size();mb/=b.size();double den=sqrt((var(a)+var(b))/2);if(den<=1e-15)return abs(ma-mb)<1e-12?0:1e9;return abs(ma-mb)/den;}
int main(int argc,char**argv){if(argc!=4){cerr<<"usage: cert census.tsv selected.txt cert.json\n";return 2;}ifstream f(argv[1]);if(!f)throw runtime_error("census");string line;getline(f,line);string expected="sha\tfamily\tside\tsquare\tsf_main\tsf_q\tsf_qshare\tberserk_main\tberserk_q\tberserk_qshare\tethereal_main\tethereal_q\tethereal_qshare\tinanis_tt_main\tinanis_pawn_q";if(line!=expected)throw runtime_error("P22_TSV_HEADER");map<string,R> rows;while(getline(f,line)){if(line.empty())continue;auto v=split(line,'\t');if(v.size()!=15)throw runtime_error("P22_TSV_WIDTH");R r;r.sha=v[0];r.fam=v[1];r.side=v[2];r.sq=v[3];for(int j=0;j<P;j++)r.z[j]=stod(v[4+j]);r.tt=stoll(v[13]);r.pq=stoll(v[14]);rows[r.sha]=r;}
 ifstream s(argv[2]);set<string> sel;while(getline(s,line)){if(!line.empty())sel.insert(line);}if(sel.size()!=96)throw runtime_error("P22_SELECTED_COUNT");map<string,int> q;vector<R> h,m;for(auto &sha:sel){if(!rows.count(sha))throw runtime_error("P22_SELECTED_UNKNOWN");auto r=rows.at(sha);if(r.tt<=0||r.pq<=0)throw runtime_error("P22_INANIS_ENGAGEMENT");q[r.fam+"|"+r.side]++;if(r.sq=="HEAVY_HEAVY")h.push_back(r);else if(r.sq=="MINOR_MINOR")m.push_back(r);else throw runtime_error("P22_SQUARE");}if(q.size()!=16)throw runtime_error("P22_STRATA");for(auto &kv:q)if(kv.second!=6)throw runtime_error("P22_QUOTA");if(h.size()!=48||m.size()!=48)throw runtime_error("P22_RELATION_COUNT");
 array<double,P>d{},lr{};double mx=0,mean=0,mvr=0;for(int j=0;j<P;j++){vector<double>a,b;for(auto&r:h)a.push_back(r.z[j]);for(auto&r:m)b.push_back(r.z[j]);d[j]=smd(a,b);mx=max(mx,d[j]);mean+=d[j];double va=var(a),vb=var(b);lr[j]=(va<=1e-15&&vb<=1e-15)?0:(va<=1e-15||vb<=1e-15?1e9:abs(log(va/vb)));mvr=max(mvr,lr[j]);}mean/=P;bool pass=mx<=TH+1e-12;
 ofstream o(argv[3]);o<<setprecision(17)<<"{\n  \"schema\": \"c3x-p22-cpp-balance-certificate-v1\",\n  \"selected_count\": 96,\n  \"heavy_count\": 48,\n  \"minor_count\": 48,\n  \"quota_pass\": true,\n  \"inanis_engagement_pass\": true,\n  \"threshold\": 0.5,\n  \"max_abs_smd\": "<<mx<<",\n  \"mean_abs_smd\": "<<mean<<",\n  \"max_abs_log_variance_ratio\": "<<mvr<<",\n  \"smd\": [";for(int j=0;j<P;j++){if(j)o<<",";o<<d[j];}o<<"],\n  \"abs_log_variance_ratio\": [";for(int j=0;j<P;j++){if(j)o<<",";o<<lr[j];}o<<"],\n  \"gate_pass\": "<<(pass?"true":"false")<<"\n}\n";cout<<"P22_CPP_CERT max_smd="<<mx<<" pass="<<pass<<"\n";return pass?0:42;}
