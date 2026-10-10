#!/usr/bin/env python3
"""C3X0.23 licence gate never converts a source download into reuse authority."""
import io,json,tempfile,unittest,zipfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_023_rights_preupload_gate import scan_payload,audit
class RightsFailClosed(unittest.TestCase):
    def test_raw_TWIC_PGN_headers_blocked(self):
        raw=b'[Event "A"]\n[White "B"]\n[Black "C"]\n\n1. e4 e5 2. Nf3 Nc6'
        self.assertIn("RESTRICTED_OR_UNREVIEWED_CHESS_GAME_SOURCE",
                      scan_payload("games.pgn",raw,"P1_SOURCE_POINTER"))
        self.assertIn("PGN_RECORD_HEADERS_NOT_CLEAR_TO_RELEASE",
                      scan_payload("fake.md",raw,"P0_AUTHORED_CODE"))
    def test_archive_with_hidden_PGN_blocked(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as f:
            f.writestr("hidden/scored.pgn",b'[Event "X"]\n1. e4 e5 *')
        res=scan_payload("harmless.zip",b.getvalue(),"P0_AUTHORED_CODE")
        self.assertTrue(any("ARCHIVE/RESTRICTED" in x for x in res),res)
    def test_unknown_zstd_held(self):
        self.assertIn("ZSTD_SOURCE_OR_BINARY_NOT_LICENSE_CHECKED",
                      scan_payload("data.txt",b"\x28\xb5\x2f\xfd", "P2_AGGREGATE_SUMMARY"))
    def test_TWIC_derived_FEN_is_review_not_autocleared(self):
        raw=b'{"source":"TWIC1664","fen4":"8/8/8/8/8/8/8/8 w - -","played_legal_move_uci":"e2e4"}'
        self.assertIn("TWIC_DERIVED_FEN_MOVE_REQUIRES_HUMAN_REVIEW",
                      scan_payload("cohort.json",raw,"P2_AGGREGATE_SUMMARY"))
    def test_aggregate_non_reconstructive_summary_passes_scan_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"summary.json"
            p.write_text(json.dumps({"TWIC_source_SHA":"a"*64,
                                       "games":16,"changed_games":5}))
            a=audit([p],"P2_AGGREGATE_SUMMARY")
            self.assertEqual(a["status"],"SCAN_PASS_NOT_A_LEGAL_LICENSE")
    def test_generic_P3_license_not_autocleared(self):
        self.assertIn("P3_REQUIRES_INDIVIDUAL_LICENSE_AND_PERMISSION_REVIEW",
                      scan_payload("licensed.json",b'{"a":1}',"P3_LICENSED_DATA"))
if __name__=="__main__":unittest.main()
