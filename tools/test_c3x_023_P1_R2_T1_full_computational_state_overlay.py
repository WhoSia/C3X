#!/usr/bin/env python3
"""P1-R2-T1 native C++ SEE window/state instrumentation contract tests."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_023_P1_R2_T1_full_computational_SEE_state_overlay import (
   patch,SIGNATURE,READ,MARK,INCLUDE,PATH_FN,CALLS)
class NativeSEEState(unittest.TestCase):
    def source_fixture(self):
        return "\n".join([INCLUDE, "namespace Stockfish {",PATH_FN,SIGNATURE,
                            READ,MARK]+list(CALLS))
    def test_all_native_search_cpp_sites_source_exactly_once(self):
        patched=patch(self.source_fixture())
        for site in ("capture_prune","quiet_prune","qsearch_prune","qsearch_futility"):
            self.assertIn(',"'+site+'",ss->ply,int(depth),int(alpha),int(beta),PvNode',patched)
        for x in ("path_exact=","source_ply=","source_depth=","source_alpha=",
                  "source_beta=","source_rule50=","source_occupancy64=",
                  "occupied_is_output_arg=","branch_direct_continuation="):
            self.assertIn(x,patched)
        self.assertIn("std::ostringstream",patched)
        with self.assertRaises(ValueError):
            patch(patched)
    def test_source_type_rejects_missing_original_actual_callsite(self):
        with self.assertRaises(ValueError):
            patch(self.source_fixture().replace('c3x022_r2_see(pos,move,Value(-95),"qsearch_prune")',""))
    def test_NO_uninitialized_see_out_bitboard_dereference(self):
        from c3x_023_P1_R2_T1_full_computational_SEE_state_overlay import MARK_NEW,READ_NEW
        self.assertIn("pos.pieces()",READ_NEW)
        self.assertNotIn("uint64_t(*occupied)",MARK_NEW)
        self.assertNotIn("*occupied",MARK_NEW)
    def test_source_parser_preserves_noninteger_ancestor_hex_sequence(self):
        p=(Path(__file__).resolve().parents[1]/"harness"/
           "c3x_018_native_TT_lineage_factorial_6_8.py").read_text()
        self.assertIn('"kind","site","path_exact"',p)
if __name__=="__main__":unittest.main()
