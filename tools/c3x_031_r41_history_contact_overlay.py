#!/usr/bin/env python3
"""Passive R41 scalar heuristic access and node-dependent draw observation.
Apply only to the exact R33 source stack in a disposable checkout.
No extra search, probe, history write, or restoration. Single-thread trace.
"""
import argparse
import hashlib
import json
from pathlib import Path

HEADER = """#include <type_traits>

namespace Stockfish {
extern thread_local bool c3x_r41_active;
void c3x_r41_access(const void*, char, int);
}
"""
HELPER = r'''
// R41: metadata outside native heuristic storage. No native mutation.
thread_local bool c3x_r41_active = false;
namespace {
struct R41Range { const char* name; const char* base; size_t size; size_t width; };
thread_local R41Range r41_ranges[4]{};
thread_local std::ofstream r41_events;
thread_local uint64_t r41_serial = 0;
}
void c3x_r41_access(const void* p, char op, int value) {
    const auto addr = reinterpret_cast<std::uintptr_t>(p);
    for (const auto& r : r41_ranges) {
        const auto base = reinterpret_cast<std::uintptr_t>(r.base);
        if (addr >= base && addr - base < r.size) {
            const auto off = addr - base;
            if (off % r.width) std::abort();
            r41_events << ++r41_serial << ' ' << r.name << ' ' << off / r.width
                       << ' ' << op << ' ' << value << '\n';
            return;
        }
    }
    // Explicitly fail the coverage gate rather than guess an identity.
    r41_events << ++r41_serial << " UNKNOWN 0 " << op << ' ' << value << '\n';
}
static void r41_begin(Thread& t, int attempt, int alpha, int beta) {
    static_assert(std::is_trivially_copyable<ButterflyHistory>::value, "main layout");
    static_assert(std::is_trivially_copyable<CapturePieceToHistory>::value, "capture layout");
    static_assert(std::is_trivially_copyable<ContinuationHistory>::value, "cont layout");
    static_assert(std::is_trivially_copyable<CounterMoveHistory>::value, "counter layout");
    static_assert(sizeof(ButterflyHistory)==2*4096*sizeof(int16_t), "main dimensions");
    static_assert(sizeof(CapturePieceToHistory)==PIECE_NB*SQUARE_NB*PIECE_TYPE_NB*sizeof(int16_t), "capture dimensions");
    static_assert(sizeof(ContinuationHistory)==PIECE_NB*SQUARE_NB*PIECE_NB*SQUARE_NB*sizeof(int16_t), "cont dimensions");
    static_assert(sizeof(CounterMoveHistory)==PIECE_NB*SQUARE_NB*sizeof(Move), "counter dimensions");
    r41_ranges[0]={"main",reinterpret_cast<const char*>(&t.mainHistory),sizeof(t.mainHistory),sizeof(int16_t)};
    r41_ranges[1]={"capture",reinterpret_cast<const char*>(&t.captureHistory),sizeof(t.captureHistory),sizeof(int16_t)};
    r41_ranges[2]={"cont",reinterpret_cast<const char*>(&t.continuationHistory),sizeof(t.continuationHistory),sizeof(int16_t)};
    r41_ranges[3]={"counter",reinterpret_cast<const char*>(&t.counterMoves),sizeof(t.counterMoves),sizeof(Move)};
    std::ofstream snap("r41_snapshot.bin",std::ios::binary|std::ios::trunc);
    std::ofstream meta("r41_layout.txt",std::ios::trunc);
    for (const auto& r : r41_ranges) {
        snap.write(r.base,r.size);
        meta << r.name << ' ' << r.size << ' ' << r.width << '\n';
    }
    snap.close(); meta.close();
    if (!snap || !meta) std::abort();
    r41_events.open("r41_events.txt",std::ios::trunc);
    if (!r41_events) std::abort();
    r41_serial=0;
    std::cerr << "C3X_R41_CP attempt=" << attempt << " root_depth=" << t.rootDepth
              << " completed=" << t.completedDepth << " alpha=" << alpha << " beta=" << beta
              << " nodes=" << t.nodes.load(std::memory_order_relaxed) << '\n';
    c3x_r41_active=true;
}
static void r41_end() {
    c3x_r41_active=false;
    r41_events.close();
    if (!r41_events) std::abort();
    std::cerr << "C3X_R41_END accesses=" << r41_serial << '\n';
}
'''
RULES = {
"movepick.h":[
    ("#include <type_traits>\n", HEADER, "decl"),
    ("  void operator=(const T& v) { entry = v; }",
     """  void operator=(const T& v) {
    entry = v;
    if constexpr (std::is_integral<T>::value || std::is_enum<T>::value)
        if (c3x_r41_active) c3x_r41_access(&entry,'W',int(entry));
  }""","assign"),
    ("  T* operator&() { return &entry; }",
     """  T* operator&() {
    if constexpr (std::is_integral<T>::value || std::is_enum<T>::value)
        if (c3x_r41_active) c3x_r41_access(&entry,'P',int(entry));
    return &entry;
  }""","address"),
    ("  T* operator->() { return &entry; }",
     """  T* operator->() {
    if constexpr (std::is_integral<T>::value || std::is_enum<T>::value)
        if (c3x_r41_active) c3x_r41_access(&entry,'P',int(entry));
    return &entry;
  }""","pointer"),
    ("  operator const T&() const { return entry; }",
     """  operator const T&() const {
    if constexpr (std::is_integral<T>::value || std::is_enum<T>::value)
        if (c3x_r41_active) c3x_r41_access(&entry,'R',int(entry));
    return entry;
  }""","read"),
    ("    entry += bonus - entry * abs(bonus) / D;",
     """    if (c3x_r41_active) c3x_r41_access(&entry,'R',int(entry));
    entry += bonus - entry * abs(bonus) / D;
    if (c3x_r41_active) c3x_r41_access(&entry,'W',int(entry));""","update")
],
"search.cpp":[
    ("#include <sstream>\n","#include <sstream>\n#include <fstream>\n#include <cstdint>\n#include <cstdlib>\n","includes"),
    ("namespace Stockfish {\n","namespace Stockfish {\n"+HELPER,"implementation"),
    ("    return VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);",
     """    const auto v = VALUE_DRAW - 1 + Value(thisThread->nodes & 0x2);
    if (c3x_r41_active)
        r41_events << ++r41_serial << " draw " << thisThread->nodes.load(std::memory_order_relaxed)
                   << " D " << int(v) << '\\n';
    return v;""","draw"),
    ("              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);",
     """              const char* r41 = std::getenv("C3X_R41_HISTORY");
              const bool r41_here = r41 && std::strcmp(r41,"1")==0 && c3x_trace() && c3xAttempt==17;
              if (r41_here) {
                  if (Threads.size()!=1 || rootDepth!=14 || completedDepth!=13 || pvIdx!=0 || Threads.stop)
                      std::abort();
                  r41_begin(*this,c3xAttempt,alpha,beta);
              }
              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);
              if (r41_here) r41_end();""","root_hook")
]
}

def transform(source, reverse=False):
    out={}
    for name,rules in RULES.items():
        s=source[name]
        for old,new,label in reversed(rules) if reverse else rules:
            if reverse: old,new=new,old
            if s.count(old)!=1: raise ValueError(f"R41_ANCHOR_{name}_{label}_{s.count(old)}")
            s=s.replace(old,new,1)
        out[name]=s
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("manifest",type=Path)
    a=p.parse_args()
    root=a.source/"src"
    old={n:(root/n).read_bytes().decode("utf-8") for n in RULES}
    new=transform(old)
    if transform(new,True)!=old: raise ValueError("R41_ROUNDTRIP")
    h=lambda s:hashlib.sha256(s.encode()).hexdigest()
    for n,s in new.items(): (root/n).write_bytes(s.encode())
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    a.manifest.write_text(json.dumps({"before":{n:h(s) for n,s in old.items()},"after":{n:h(s) for n,s in new.items()},"roundtrip":True,"scope":"scalar history access; root attempt17; no restoration"},indent=2)+"\n")

if __name__=="__main__":main()
