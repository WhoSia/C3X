#!/usr/bin/env python3
"""Add the CSWP first candidate and frame-entry alpha/beta observer.
Requires Stockfish16 plus the validated passive PIN and root-object SEE patch.
Observational only. Do not alter legal moves, SEE return, or TT table layout.
"""
import argparse,json,hashlib
from pathlib import Path
def one(s,a,b,name):
    n=s.count(a)
    if n!=1:raise RuntimeError('C3X015_CSWP_SOURCE_ANCHOR_'+name+'_'+str(n))
    return s.replace(a,b,1)
def patch(root):
    p=Path(root)/'src';hd=p/'c3x014_pin_trace.h';ps=p/'position.cpp';ss=p/'search.cpp'
    raw={f.name:f.read_bytes() for f in (hd,ps,ss)}
    h=raw[hd.name].decode();c=raw[ps.name].decode();s=raw[ss.name].decode()
    h=one(h,'#include <cstdint>','#include <cstdint>\n#include <string>','HEADER')
    h=one(h,'extern C3X014RootObjectSEE c3x014_root_obj;', '''extern C3X014RootObjectSEE c3x014_root_obj;
struct C3X015SearchFrame { std::uint64_t key=0; int alpha=0,beta=0,depth=0,node_kind=-1; };
struct C3X015SearchScope {
  C3X015SearchFrame previous;
  C3X015SearchScope(std::uint64_t k,int a,int b,int d,int node);
  ~C3X015SearchScope();
};
void c3x015_window_reset();
void c3x015_potential_root_see_site(std::uint64_t key);
std::string c3x015_window_summary();''','HEADER_CSWP')
    c=one(c,'#include "position.h"','#include "position.h"\n#include <sstream>\n#include <vector>','CPP_INCLUDE')
    c=one(c,'C3X014RootObjectSEE c3x014_root_obj;', '''C3X014RootObjectSEE c3x014_root_obj;
struct C3X015WindowObserver {
  std::uint64_t search_enter_count=0,prefix_hash=1469598103934665603ULL;
  std::uint64_t candidate_count=0,first_pos_key=0,first_search_ordinal=0;
  C3X015SearchFrame first_frame;
  bool first_seen=false;
  std::vector<std::string> after_search_frames;
};
static thread_local C3X015WindowObserver c3x015_win;
static thread_local C3X015SearchFrame c3x015_active_frame;
static void c3x015_mix(std::uint64_t k) {
  c3x015_win.prefix_hash^=k;
  c3x015_win.prefix_hash*=1099511628211ULL;
}
void c3x015_window_reset() {
  c3x015_win=C3X015WindowObserver{};
  c3x015_active_frame=C3X015SearchFrame{};
}
C3X015SearchScope::C3X015SearchScope(std::uint64_t k,int a,int b,int d,int node) {
  previous=c3x015_active_frame;
  c3x015_active_frame={k,a,b,d,node};
  ++c3x015_win.search_enter_count;
  if (!c3x015_win.first_seen) {
    c3x015_mix(k);c3x015_mix(std::uint64_t(std::uint32_t(a)));
    c3x015_mix(std::uint64_t(std::uint32_t(b)));
    c3x015_mix(std::uint64_t(std::uint32_t(d)));
    c3x015_mix(std::uint64_t(std::uint32_t(node)));
  } else if (c3x015_win.after_search_frames.size()<4096) {
    std::ostringstream line;
    line<<std::hex<<k<<std::dec<<":"<<a<<":"<<b<<":"<<d<<":"<<node;
    c3x015_win.after_search_frames.push_back(line.str());
  }
}
C3X015SearchScope::~C3X015SearchScope(){c3x015_active_frame=previous;}
void c3x015_potential_root_see_site(std::uint64_t key) {
  ++c3x015_win.candidate_count;
  if (!c3x015_win.first_seen) {
    c3x015_win.first_seen=true;
    c3x015_win.first_pos_key=key;
    c3x015_win.first_search_ordinal=c3x015_win.search_enter_count;
    c3x015_win.first_frame=c3x015_active_frame;
  }
}
std::string c3x015_window_summary() {
  std::ostringstream s;
  s<<"candidate_count="<<c3x015_win.candidate_count
   <<" first_candidate="<<int(c3x015_win.first_seen)
   <<" first_key="<<c3x015_win.first_pos_key
   <<" first_search_ordinal="<<c3x015_win.first_search_ordinal
   <<" prefix_fnv64="<<c3x015_win.prefix_hash
   <<" search_enter_total="<<c3x015_win.search_enter_count
   <<" frame_key="<<c3x015_win.first_frame.key
   <<" entry_alpha="<<c3x015_win.first_frame.alpha
   <<" entry_beta="<<c3x015_win.first_frame.beta
   <<" entry_depth="<<c3x015_win.first_frame.depth
   <<" entry_node_type="<<c3x015_win.first_frame.node_kind
   <<" post_search_entries="<<c3x015_win.after_search_frames.size()<<" stream=";
  for (auto& e:c3x015_win.after_search_frames)s<<e<<"|";
  return s.str();
}''','CPP_OBSERVER')
    anchor='''          Bitboard c3x014_SEE_exclusions=blockers_for_king(stm);
          if (c3x014_root_obj.arm==1'''
    replace='''          Bitboard c3x014_SEE_exclusions=blockers_for_king(stm);
          if (c3x014_root_obj.arm>=0 && stm==c3x014_root_obj.root_pinned_side
              && c3x014_root_obj.pinned_square>=0 && c3x014_root_obj.pinner_square>=0) {
            const Square p=Square(c3x014_root_obj.pinned_square);
            const Square a=Square(c3x014_root_obj.pinner_square);
            const Bitboard pb=square_bb(p), ab=square_bb(a);
            if ((stmAttackers&pb) && (c3x014_SEE_exclusions&pb)
                && piece_on(p)==c3x014_root_obj.root_pinned_piece
                && piece_on(a)==c3x014_root_obj.root_pinner_piece
                && int(square<KING>(stm))==c3x014_root_obj.king_square
                && (pinners(~stm)&ab) && (occupied&ab))
              c3x015_potential_root_see_site(std::uint64_t(key()));
          }
          if (c3x014_root_obj.arm==1'''
    c=one(c,anchor,replace,'SEE_CANDIDATE_EXACT_MATCH')
    s=one(s,'  c3x014_root_object_prepare(rootPos);','  c3x015_window_reset();\n  c3x014_root_object_prepare(rootPos);','ROOT_RESET')
    s=one(s,'  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {\n',
        '  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {\n    C3X015SearchScope c3x015_scope(std::uint64_t(pos.key()),int(alpha),int(beta),int(depth),int(nodeType));\n','MAIN_SCOPE')
    s=one(s,'  Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {\n',
        '  Value qsearch(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth) {\n    C3X015SearchScope c3x015_scope(std::uint64_t(pos.key()),int(alpha),int(beta),int(depth),int(nodeType));\n','QS_SCOPE')
    s=one(s,'            << " target_fired=" << c3x014_root_obj.fired\n            << sync_endl;',
        '            << " target_fired=" << c3x014_root_obj.fired\n            << sync_endl;\n  sync_cout << "info string c3x015_first_site_window " << c3x015_window_summary() << sync_endl;', 'UCI_TRACE')
    for f,body in ((hd,h),(ps,c),(ss,s)):f.write_text(body)
    return {'schema':'c3x-015-cswp-source-native-entry-window-and-first-SEE-site-context-v1',
            'scope':'observational search-frame-entry alpha,beta and candidate in OFF/ON, bounded 4096 post-candidate search enters; no first TT causal mediation proven',
            'source_sha':{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()},
            'patched_sha':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (hd,ps,ss)}}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--out-manifest',required=True)
    args=ap.parse_args();info=patch(args.source);dest=Path(args.out_manifest)
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(info,indent=2)+'\n')
    print('C3X015_CSWP_FIRST_SITE_WINDOW_SOURCE_OBSERVER_PATCH_PASS',flush=True)
