#!/usr/bin/env python3
"""CSWP P4: add exact physical-TT writer/reader and alpha-beta probe/cutoff
event tracing to the preverified Stockfish16 P3 R2 observer. Not a TT intervention.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,k):
 n=s.count(a)
 if n!=1:raise RuntimeError('CSWP_P4_ANCHOR_'+k+'_'+str(n))
 return s.replace(a,b,1)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--source',required=True);ap.add_argument('--out-manifest',required=True)
 a=ap.parse_args();p=Path(a.source)/'src'
 files={n:p/n for n in ('tt.h','tt.cpp','position.cpp','search.cpp','c3x014_pin_trace.h')}
 raw={n:f.read_bytes() for n,f in files.items()}
 h,tt,pos,s,th=(raw[n].decode() for n in files)
 h=one(h,'extern TranspositionTable TT;',r"""
// P4 physically exact full-key sidecar; original 10-byte TTEntry unchanged.
struct C3X015LastWriter {
  Key full_key=0;
  std::uint64_t sequence=0;
  int tag=0, bound=0, depth=0, known=0, key_exact=0, reused=0;
};
C3X015LastWriter c3x015_tt_writer(const TTEntry* slot,Key key);
void c3x015_tt_reset();
void c3x015_tt_labeled_save(TTEntry* slot,int tag,Key key,Value v,bool pv,Bound b,Depth d,Move m,Value eval);
extern TranspositionTable TT;""",'TT_HEADER')
 tt=one(tt,'#include <thread>','#include <thread>\n#include <unordered_map>\n#include <cstdint>','TT_INC')
 tt=one(tt,'TranspositionTable TT; // Our global transposition table',r"""TranspositionTable TT; // Our global transposition table
struct C3X015TTSlot { Key key=0;std::uint64_t sequence=0;int tag=0,bound=0,depth=0,reused=0;bool known=false; };
static thread_local std::unordered_map<const TTEntry*,C3X015TTSlot> c3x015_writers;
static thread_local std::uint64_t c3x015_tt_sequence=0;
static thread_local int c3x015_writer_tag=0;
void c3x015_tt_reset(){c3x015_writers.clear();c3x015_tt_sequence=0;c3x015_writer_tag=0;}
void c3x015_tt_record(const TTEntry*slot,Key k,Bound b,Depth d,bool full) {
  ++c3x015_tt_sequence;
  if(!full)return;
  C3X015TTSlot& x=c3x015_writers[slot];
  if(x.known && x.key!=k)++x.reused;
  x.known=true;x.key=k;x.tag=c3x015_writer_tag;
  x.bound=int(b);x.depth=int(d);x.sequence=c3x015_tt_sequence;
}
C3X015LastWriter c3x015_tt_writer(const TTEntry*slot,Key key) {
  C3X015LastWriter z;
  auto it=c3x015_writers.find(slot);
  if(it==c3x015_writers.end() || !it->second.known)return z;
  const auto& w=it->second;
  z.full_key=w.key;z.sequence=w.sequence;z.tag=w.tag;z.bound=w.bound;
  z.depth=w.depth;z.known=1;z.key_exact=int(w.key==key);z.reused=w.reused;
  return z;
}
void c3x015_tt_labeled_save(TTEntry*e,int tag,Key k,Value v,bool pv,Bound b,Depth d,Move m,Value ev) {
  const int prev=c3x015_writer_tag;
  c3x015_writer_tag=tag;e->save(k,v,pv,b,d,m,ev);c3x015_writer_tag=prev;
}""",'TT_SIDECAR')
 tt=one(tt,"  if (   b == BOUND_EXACT\n      || (uint16_t)k != key16\n      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4)\n  {",
 """  const bool c3x015_full_fields = (b == BOUND_EXACT
      || (uint16_t)k != key16
      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4);
  if (c3x015_full_fields)
  {""",'TT_WRITE_BRANCH')
 tt=one(tt,"      eval16    = (int16_t)ev;\n  }\n}","      eval16    = (int16_t)ev;\n  }\n  c3x015_tt_record(this,k,b,d,c3x015_full_fields);\n}",'TT_WRITE_RECORD')
 th=one(th,'void c3x015_window_reset();','void c3x015_window_reset();\nvoid c3x015_record_tt(Key key,TTEntry* slot,bool hit,int value,int alpha,int beta,int depth,int ply,int kind,int cutoff);\nstd::string c3x015_tt_summary();','P4_API')
 th=one(th,'class Position;','class Position;\nstruct TTEntry;','TT_FORWARD')
 pos=one(pos,'#include <vector>','#include <vector>\n#include <string>','POS_INC')
 pos=one(pos,'static thread_local C3X015SearchFrame c3x015_active_frame;',r"""static thread_local C3X015SearchFrame c3x015_active_frame;
struct C3X015TTProvenance {
  std::uint64_t probes=0,reported=0,key_exact=0,missing_writer=0,taken_cutoffs=0;
  std::vector<std::string> events;
};
static thread_local C3X015TTProvenance c3x015_tt_events;
void c3x015_record_tt(Key key,TTEntry* slot,bool hit,int val,int alpha,int beta,int depth,int ply,int kind,int cutoff){
  if(!c3x015_win.first_seen)return;
  ++c3x015_tt_events.probes;
  if(cutoff)++c3x015_tt_events.taken_cutoffs;
  if(c3x015_tt_events.events.size()>=2048)return;
  C3X015LastWriter w=c3x015_tt_writer(slot,key);
  if(hit && !w.known)++c3x015_tt_events.missing_writer;
  if(hit && w.key_exact)++c3x015_tt_events.key_exact;
  std::ostringstream o;
  o<<std::hex<<std::uint64_t(key)<<std::dec<<":"<<kind<<":"<<ply<<":"<<depth
    <<":"<<alpha<<":"<<beta<<":"<<int(hit)<<":"<<val<<":"<<cutoff
    <<":"<<w.known<<":"<<w.key_exact<<":"<<w.tag<<":"<<w.bound<<":"<<w.depth
    <<":"<<w.sequence<<":"<<w.reused;
  c3x015_tt_events.events.push_back(o.str());
  ++c3x015_tt_events.reported;
}
std::string c3x015_tt_summary(){
  std::ostringstream o;
  o<<"probes="<<c3x015_tt_events.probes<<" listed="<<c3x015_tt_events.reported
   <<" key_exact="<<c3x015_tt_events.key_exact
   <<" unknown_writer="<<c3x015_tt_events.missing_writer
   <<" taken_cutoffs="<<c3x015_tt_events.taken_cutoffs<<" stream=";
  for(const auto&e:c3x015_tt_events.events)o<<e<<"|";
  return o.str();
}""",'P4_REPORTER')
 pos=one(pos,'  c3x015_win=C3X015WindowObserver{};','  c3x015_win=C3X015WindowObserver{};\n  c3x015_tt_events=C3X015TTProvenance{};\n  c3x015_tt_reset();','P4_RESET')
 if s.count('tte->save(')!=6:raise RuntimeError('TT_SIX_SAVE_SOURCE_CENSUS_CHANGED_'+str(s.count('tte->save(')))
 # Six original source sites: tablebase/static eval/ProbCut/main terminal/qsearch early/qsearch terminal.
 for tag in range(1,7):
  s=s.replace('tte->save(',f'c3x015_tt_labeled_save(tte, {tag}, ',1)
 needle='    ttValue = ss->ttHit ? value_from_tt(tte->value(), ss->ply, pos.rule50_count()) : VALUE_NONE;'
 if s.count(needle)!=2:raise RuntimeError('TT_READ_SOURCE_SITE_COUNT_'+str(s.count(needle)))
 s=s.replace(needle,
 '''    ttValue = ss->ttHit ? value_from_tt(tte->value(), ss->ply, pos.rule50_count()) : VALUE_NONE;
    c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),0);''','MAIN_READ')
 # second main and qsearch instance still left
 s=one(s,needle,
 '''    ttValue = ss->ttHit ? value_from_tt(tte->value(), ss->ply, pos.rule50_count()) : VALUE_NONE;
    c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),0);''','QS_READ')
 s=one(s,'        if (pos.rule50_count() < 90)\n            return ttValue;',
 """        if (pos.rule50_count() < 90) {
            c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),1);
            return ttValue;
        }""",'MAIN_CUTOFF')
 s=one(s,'        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))\n        return ttValue;',
 """        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER))) {
        c3x015_record_tt(posKey,tte,ss->ttHit,int(ttValue),int(alpha),int(beta),int(depth),int(ss->ply),int(nodeType),1);
        return ttValue;
    }""",'QS_CUTOFF')
 s=one(s,'  sync_cout << "info string c3x015_first_site_window " << c3x015_window_summary() << sync_endl;',
 '  sync_cout << "info string c3x015_first_site_window " << c3x015_window_summary() << sync_endl;\n  sync_cout << "info string c3x015_tt_provenance " << c3x015_tt_summary() << sync_endl;','UCI_P4')
 for n,v in [('tt.h',h),('tt.cpp',tt),('position.cpp',pos),('search.cpp',s),('c3x014_pin_trace.h',th)]:
  files[n].write_text(v)
 output={"schema":"c3x015-source-native-cswp-TT-physical-writer-bound-reader-window-v1",
         "source":"SF16 plus passive PIN object-guard SEE and P3R2 frame-trace; no TT move/bound semantics changed",
         "tags":{"1":"MAIN_TABLEBASE","2":"MAIN_STATIC_EVAL","3":"MAIN_PROBCUT","4":"MAIN_TERMINAL","5":"QSEARCH_EARLY","6":"QSEARCH_TERMINAL"},
         "limits":["Records first 2048 TT read/cutoff events after first eligible SEE, full-key sidecar","Mediating necessity still requires independent TT-return intervention","One thread only; TTEntry physical layout unmodified"],
         "original_sha256":{n:hashlib.sha256(b).hexdigest() for n,b in raw.items()},
         "patched_sha256":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in files}}
 dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(output,indent=2)+"\n")
 print("C3X015_P4_TT_WRITER_READER_ALPHA_BETA_SOURCE_PATCH_APPLIED",flush=True)
if __name__=="__main__":main()
