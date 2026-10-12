#!/usr/bin/env python3
"""Reversible minimal observer of Stockfish 16 actual TT writes, qsearch reads, UCI d."""
import sys, json
from pathlib import Path

def once(s, a, b, name):
    if s.count(a) != 1:
        raise RuntimeError(name+" anchor count "+str(s.count(a)))
    return s.replace(a,b,1)

writer = '''
struct C3XP8Writer { Key full; int raw, bound, depth; unsigned long long serial; };
static thread_local std::unordered_map<const TTEntry*, C3XP8Writer> c3xp8_writers;
static thread_local unsigned long long c3xp8_serial=0;
void c3xp8_read(const TTEntry* t, Key key, int returned, int beta, int ply, int rule50, int rep) {
    static thread_local int count=0;
    if(count++>=4) return;
    const auto it=c3xp8_writers.find(t);
    bool known=it!=c3xp8_writers.end();
    bool same=known && it->second.full==key;
    bool raw=known && it->second.raw==int(t->value());
    sync_cout << "info string c3xp8_tt_return known=" << int(known)
       << " same_fullkey=" << int(same) << " same_raw=" << int(raw)
       << " serial=" << (known?it->second.serial:0)
       << " writer_bound=" << (known?it->second.bound:-1)
       << " reader_bound=" << int(t->bound())
       << " writer_depth=" << (known?it->second.depth:-99)
       << " reader_depth=" << int(t->depth())
       << " value=" << returned << " beta=" << beta
       << " side=" << (returned>=beta?"LOWER":"UPPER")
       << " ply=" << ply << " rule50=" << rule50 << " repetition=" << rep << sync_endl;
}
'''
oldQ = '''    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;'''
newQ = oldQ.replace('        return ttValue;',
'''    {
        c3xp8_read(tte,posKey,int(ttValue),int(beta),int(ss->ply),
                   int(pos.rule50_count()),int(pos.state()->repetition));
        return ttValue;
    }''')
oldD = 'else if (token == "d")        sync_cout << pos << sync_endl;'
newD = '''else if (token == "d")
      {
          sync_cout << pos << sync_endl;
          sync_cout << "info string c3xp8_history repetition=" << pos.state()->repetition
                    << " rule50=" << pos.rule50_count()
                    << " draw0=" << int(pos.is_draw(0))
                    << " repeated=" << int(pos.has_repeated()) << sync_endl;
      }'''
def changed(original):
    tt=original["tt.cpp"]
    tt=once(tt,'#include <thread>','#include <thread>\n#include <unordered_map>',"include")
    tt=once(tt,'TranspositionTable TT; // Our global transposition table',
        'TranspositionTable TT; // Our global transposition table\n'+writer,"writer state")
    tt=once(tt,'      eval16    = (int16_t)ev;',
      '      eval16    = (int16_t)ev;\n      c3xp8_writers[this] = {k,int(value16),int(b),int(d),++c3xp8_serial};',"write")
    search=once(original["search.cpp"],'namespace Stockfish {\n',
       'namespace Stockfish {\nvoid c3xp8_read(const TTEntry*,Key,int,int,int,int,int);\n',"reader signature")
    search=once(search,oldQ,newQ,"original bounded qsearch")
    uci=once(original["uci.cpp"],oldD,newD,"UCI history")
    return dict(zip(original, [tt,search,uci]))
def main():
    root=Path(sys.argv[1]);output=Path(sys.argv[2])
    names={"tt.cpp":root/"src/tt.cpp","search.cpp":root/"src/search.cpp","uci.cpp":root/"src/uci.cpp"}
    old={k:v.read_text() for k,v in names.items()}
    new=changed(old)
    for k,v in new.items():
        if old[k]==v:raise AssertionError("missing original observer code")
        names[k].write_text(v)
    output.write_text(json.dumps({"source":"official Stockfish16","actual_TT_overwrite":True,
      "actual_qsearch_return":True,"source_output_minimal":True,
      "proven_true_chess_bound":False,"original_history_observer":True},indent=2)+"\n")
    print("C3XP8_ORIGINAL_SOURCE_SITES_PATCHED")
if __name__=="__main__":main()
