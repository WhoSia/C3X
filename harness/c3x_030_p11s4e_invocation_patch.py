#!/usr/bin/env python3
"""C3X 0.30 P11/S4E — scope-based invocation identity, read-only Stockfish16.

Source-anchored patch adds a thread-local invocation stack and a per-node RAII
scope for all main-search<> returns, including early exits. It does not cover
qsearch, nor claim value-transfer mediation. Root candidate logs include the
last finished main-search child invocation id, NOT proof this child contributed
to the score, which requires a later explicit edge/gate.
"""
import argparse, hashlib
from pathlib import Path

NS="namespace Stockfish {\n\nnamespace Search {"
ENTRY="""  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {

    constexpr bool PvNode = nodeType != NonPV;
    constexpr bool rootNode = nodeType == Root;"""
PROBE="""    excludedMove = ss->excludedMove;
    posKey = pos.key();
    tte = TT.probe(posKey, ss->ttHit);"""
RET="""    assert(bestValue > -VALUE_INFINITE && bestValue < VALUE_INFINITE);

    return bestValue;
  }


  // qsearch()"""
ROOT="""          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);"""
HEADER="""namespace Stockfish {

// Thread-local process-wide sequence distinguishes iterations with same raw move.
static thread_local unsigned long long c3x_e_next_id = 0;
static thread_local unsigned long long c3x_e_stack[MAX_PLY + 8] = {};
static thread_local unsigned long long c3x_e_last_child[MAX_PLY + 8] = {};
static thread_local unsigned c3x_e_logs = 0;

struct C3XInvocationScope {
    int ply;
    unsigned long long id;
    unsigned long long parent_id;
    bool interested = false;
    C3XInvocationScope(int p) : ply(p),
      id(++c3x_e_next_id),
      parent_id(p > 0 && p < MAX_PLY + 8 ? c3x_e_stack[p - 1] : 0) {
        if (p >= 0 && p < MAX_PLY + 8)
            c3x_e_stack[p] = id;
    }
    ~C3XInvocationScope() {
        if (ply >= 0 && ply < MAX_PLY + 8) {
            c3x_e_last_child[ply] = id;
            c3x_e_stack[ply] = 0;
        }
        // Destructor is called even on early returns; value is NOT recoverable.
        if (interested && c3x_e_logs++ < 240)
            std::cerr << "C3X_S4E kind=scope_exit id=" << id
                      << " parent=" << parent_id << " ply=" << ply
                      << " value_known=0" << std::endl;
    }
};

namespace Search {"""
ENTRY_PATCH="""  Value search(Position& pos, Stack* ss, Value alpha, Value beta, Depth depth, bool cutNode) {

    constexpr bool PvNode = nodeType != NonPV;
    constexpr bool rootNode = nodeType == Root;
    // Scope spans all main-search exit paths, including early cutoffs.
    C3XInvocationScope c3x_e_scope(ss->ply);"""
PROBE_PATCH="""    excludedMove = ss->excludedMove;
    posKey = pos.key();
    tte = TT.probe(posKey, ss->ttHit);
    static const unsigned long long c3x_e_target = []() -> unsigned long long {
        const char* s = std::getenv("C3X_S4E_KEY");
        return s ? std::strtoull(s, nullptr, 10) : 0ULL;
    }();
    if (c3x_e_target && ss->ply == 1 && static_cast<unsigned long long>(posKey) == c3x_e_target) {
        c3x_e_scope.interested = true;
        if (c3x_e_logs++ < 240)
            std::cerr << "C3X_S4E kind=probe id=" << c3x_e_scope.id
                      << " parent=" << c3x_e_scope.parent_id
                      << " key=" << posKey << " hit=" << int(ss->ttHit)
                      << " ply=" << ss->ply << " depth=" << depth << std::endl;
    }"""
RET_PATCH="""    assert(bestValue > -VALUE_INFINITE && bestValue < VALUE_INFINITE);
    if (c3x_e_scope.interested && c3x_e_logs++ < 240)
        std::cerr << "C3X_S4E kind=normal_return id=" << c3x_e_scope.id
                  << " parent=" << c3x_e_scope.parent_id << " ply=" << ss->ply
                  << " value=" << bestValue << std::endl;
    return bestValue;
  }


  // qsearch()"""
ROOT_PATCH="""          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);
          if (c3x_e_target && c3x_e_logs++ < 240)
              std::cerr << "C3X_S4E kind=root_candidate id=" << c3x_e_scope.id
                        << " child_last=" << c3x_e_last_child[ss->ply + 1]
                        << " root_move_raw=" << static_cast<int>(move)
                        << " value=" << value << " old_best=" << bestValue
                        << " depth=" << depth << std::endl;"""

def sha(b):return hashlib.sha256(b).hexdigest()
def apply(s):
    if "C3X_S4E kind=" in s:raise ValueError("S4E_HOLD_DOUBLE_PATCH")
    probes=s.count("tte = TT.probe(posKey, ss->ttHit);")
    saves=s.count("tte->save(")
    for old,new in (("#include <algorithm>","#include <algorithm>\n#include <cstdlib>"),
                    (NS,HEADER),(ENTRY,ENTRY_PATCH),(PROBE,PROBE_PATCH),
                    (RET,RET_PATCH),(ROOT,ROOT_PATCH)):
        if s.count(old)!=1:
            raise ValueError("S4E_HOLD_NONUNIQUE_STOCKFISH16_SOURCE_SITE:"+str(s.count(old)))
        s=s.replace(old,new,1)
    if s.count("tte = TT.probe(posKey, ss->ttHit);")!=probes or s.count("tte->save(")!=saves:
        raise ValueError("S4E_HOLD_UPSTREAM_TT_CALL_LOSS")
    if s.count("C3X_S4E kind=")!=4:
        raise ValueError("S4E_HOLD_TRACE_CLASSES")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    result=apply(raw.decode("utf8")).encode("utf8")
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(result)
    print("S4E_UPSTREAM_SHA",sha(raw),"S4E_READONLY_PATCH_SHA",sha(result))
if __name__=="__main__":main()
