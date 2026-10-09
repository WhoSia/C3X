#!/usr/bin/env python3
"""C3X016-P4 single-source root ordering intervention. Strict SF16 source anchors.
Same legal root move set and original relative order of all NON-target moves.
"""
import argparse, hashlib, json
from pathlib import Path

def one(s, old, new, name):
    n=s.count(old)
    if n!=1: raise RuntimeError(f"P4_{name}_SOURCE_ANCHOR_COUNT_{n}")
    return s.replace(old,new,1)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out-manifest",required=True)
    args=a.parse_args()
    f=Path(args.source)/"src/search.cpp"
    old=f.read_bytes()
    src=old.decode()
    needle="  Color us = rootPos.side_to_move();\n  int iterIdx = 0;"
    replace=r"""  Color us = rootPos.side_to_move();
  // C3X 0.16 P4 source-exact, played-legal move ordering intervention.
  // Must run before the very first iterative deepening pass. Never alter legality.
  const char* c3x_p4_mode = std::getenv("C3X016_P4_MODE");
  const char* c3x_p4_fen4 = std::getenv("C3X016_P4_FEN4");
  const char* c3x_p4_played = std::getenv("C3X016_P4_PLAYED_NATIVE");
  if (!c3x_p4_mode || !c3x_p4_fen4 || !c3x_p4_played)
      std::abort();
  std::string c3x_p4_kind(c3x_p4_mode);
  if (c3x_p4_kind != "O" && c3x_p4_kind != "F" && c3x_p4_kind != "Z")
      std::abort();
  std::string c3x_p4_board(rootPos.fen());
  std::string c3x_p4_expected(c3x_p4_fen4);
  if (c3x_p4_board.size() <= c3x_p4_expected.size()
      || c3x_p4_board.compare(0,c3x_p4_expected.size(),c3x_p4_expected)
      || c3x_p4_board[c3x_p4_expected.size()] != ' ')
      std::abort();
  int c3x_p4_selected=std::atoi(c3x_p4_played);
  auto c3x_p4_selected_it=std::find_if(rootMoves.begin(),rootMoves.end(),
    [c3x_p4_selected](const RootMove& r){return int(r.pv[0])==c3x_p4_selected;});
  if(c3x_p4_selected_it==rootMoves.end())
      std::abort(); // Independently Go-certified selected move not present in real native legal roots.
  const int c3x_p4_original_index=int(c3x_p4_selected_it-rootMoves.begin());
  const int c3x_p4_active_move=(c3x_p4_kind=="Z" ? 99999 : c3x_p4_selected);
  auto c3x_p4_active_it=std::find_if(rootMoves.begin(),rootMoves.end(),
    [c3x_p4_active_move](const RootMove& r){return int(r.pv[0])==c3x_p4_active_move;});
  const bool c3x_p4_contact=(c3x_p4_active_it!=rootMoves.end());
  const int c3x_p4_active_index=c3x_p4_contact ? int(c3x_p4_active_it-rootMoves.begin()) : -1;
  const bool c3x_p4_shift=(c3x_p4_kind=="F" && c3x_p4_contact && c3x_p4_active_index>0);
  if (c3x_p4_shift)
      std::rotate(rootMoves.begin(),c3x_p4_active_it,c3x_p4_active_it+1);
  sync_cout << "info string c3x016_p4_root_order mode=" << c3x_p4_kind
     << " guard=1 root_legal_count=" << rootMoves.size()
     << " selected_native=" << c3x_p4_selected
     << " selected_pre_index=" << c3x_p4_original_index
     << " target_contact=" << int(c3x_p4_contact)
     << " target_pre_index=" << c3x_p4_active_index
     << " source_reorder=" << int(c3x_p4_shift)
     << " new_front_native=" << int(rootMoves[0].pv[0]) << sync_endl;
  int iterIdx = 0;"""
    src=one(src,needle,replace,"ITERATION_ENTRY")
    f.write_text(src)
    j={"schema":"c3x016-P4-SF16-single-root-target-order-source-patch-v1",
       "official_source":"Stockfish 16 sf_16 68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "search_cpp_old_sha256":hashlib.sha256(old).hexdigest(),
       "search_cpp_patched_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
       "treatments":["O unchanged","F selected legal native move rotated to first","Z impossible native sentinel no-contact"],
       "read_only_controls":"O and Z identical complete UCI; patched O vs unmodified upstream original UCI",
       "limits":["Changes original root candidate search order only and never legal move set","No named motif source operator or learned network concept is identified","F when already first has no actual reordering and remains in denominator","FEN standalone loses full source game history and repetition context"]}
    p=Path(args.out_manifest);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(j,indent=2)+"\n")
    print("C3X016_P4_SOURCE_EXACT_ROOT_ORDER_PATCH_PASS")

if __name__=="__main__":
    main()
