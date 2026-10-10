#!/usr/bin/env python3
"""Guard exact Stockfish16 search/qsearch entry and SEE actual path fingerprint."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_023_P1_native_SEE_parent_path_key_overlay import patch,MAIN,QS,LOG
class NativeKeyPath(unittest.TestCase):
    def test_exact_main_qsearch_and_SEE_observer_once(self):
        src='#include <algorithm>\nnamespace Stockfish {\n'+MAIN+"\n"+QS+"\n"+LOG
        t=patch(src)
        self.assertEqual(t.count("C3X023_AncestorGuard c3x023_node_entry(pos.key());"),2)
        for a in ("path_hash=","path_length=","parent_key64=","c3x023_native_path_fingerprint"):
            self.assertIn(a,t)
        with self.assertRaises(ValueError):patch(t)
    def test_missing_actual_source_return_fails(self):
        with self.assertRaises(ValueError):
            patch('#include <algorithm>\nnamespace Stockfish {\n'+MAIN+'\n'+QS)
    def test_never_changes_SEE_results_according_to_overlay(self):
        s=(Path(__file__).resolve().parents[1]/"tools"/
            "c3x_023_P1_native_SEE_parent_path_key_overlay.py").read_text()
        self.assertNotIn("return !original",s)
        self.assertIn('no_change_to_stockfish_original_SEE_return',s)
        self.assertIn('collision assumption',s.lower())
if __name__=="__main__":unittest.main()
