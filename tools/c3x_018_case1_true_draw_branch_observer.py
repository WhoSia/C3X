#!/usr/bin/env python3
"""Source-exact SF16 draw and game-cycle branch witness in original history.

Overlay after P4, root trace, trial, physical TT and root TT context patch.
Observer calls the same predicate once in the original boolean condition;
draw/beta branch semantics otherwise unchanged. Limited print, no mutation.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError("C3X018_DRAW_"+label+"_SOURCE_COUNT_"+str(n))
 return s.replace(a,b,1)
HEADER=r"""
// C3X018 draw predicate observer, one search worker.
namespace {
unsigned long long c3x018_draw_event_counter = 0;
bool c3x018_draw_check(Position& pos, int ply, const char* site) {
    const bool yes = pos.is_draw(ply);
    if (yes && ++c3x018_draw_event_counter <= 240)
        sync_cout << "info string c3x018_draw_probe"
                  << " type=immediate" << " site=" << site
                  << " root_call=" << c3x018_root_context_call
                  << " root_move=" << c3x018_root_context_move
                  << " poskey64=" << uint64_t(pos.key())
                  << " rule50=" << pos.rule50_count()
                  << " ply=" << ply
                  << " has_repeated=" << int(pos.has_repeated())
                  << " result=1" << sync_endl;
    return yes;
}
bool c3x018_cycle_check(Position& pos, int ply) {
    const bool yes = pos.has_game_cycle(ply);
    if (yes && ++c3x018_draw_event_counter <= 240)
        sync_cout << "info string c3x018_draw_probe"
                  << " type=upcoming_cycle" << " site=main"
                  << " root_call=" << c3x018_root_context_call
                  << " root_move=" << c3x018_root_context_move
                  << " poskey64=" << uint64_t(pos.key())
                  << " rule50=" << pos.rule50_count()
                  << " ply=" << ply
                  << " has_repeated=" << int(pos.has_repeated())
                  << " result=1" << sync_endl;
    return yes;
}
} // C3X018_DRAW_OBSERVER
"""
def patch(s):
 s=one(s,"namespace Stockfish {","namespace Stockfish {\n"+HEADER,"HEADER")
 s=one(s,"&& pos.has_game_cycle(ss->ply))","&& c3x018_cycle_check(pos,ss->ply))","CYCLE")
 # Observed each of main and qsearch exactly once
 needle="pos.is_draw(ss->ply)"
 if s.count(needle)!=2:raise RuntimeError("C3X018_DRAW_IMMEDIATE_EXPECTED_TWO")
 # Distinct first and second sites, preserves evaluation order.
 s=s.replace(needle,'c3x018_draw_check(pos,ss->ply,"main")',1)
 s=s.replace(needle,'c3x018_draw_check(pos,ss->ply,"qsearch")',1)
 return s
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/search.cpp"
 original=f.read_bytes();altered=patch(original.decode()).encode();f.write_bytes(altered)
 dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps({
 "schema":"c3x018-case1-repeat-and-immediate-draw-native-observer-v1",
 "source_before_sha256":hashlib.sha256(original).hexdigest(),
 "source_after_sha256":hashlib.sha256(altered).hexdigest(),
 "sites":["main.has_game_cycle","main.is_draw","qsearch.is_draw"],
 "observed_predicates":["pos.key full64","rule50","ply","has_repeated","root trial call","root candidate"],
 "limit":"at most first 240 positive draw/cycle branch events, never infer absence after censor",
 "authority":"Branch was true if event emitted; observer side-effects only on stdout and a counter; no unique TT mediation"}
 ,indent=2)+"\n")
 print("C3X018_NATIVE_TRUE_DRAW_PREDICATES_PATCHED")
if __name__=="__main__":main()
