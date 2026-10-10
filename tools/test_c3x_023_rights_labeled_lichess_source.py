#!/usr/bin/env python3
"""C3X0.23 new licensed-source gate must preserve Lichess licence split."""
import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from c3x_023_rights_preupload_gate import licensed_lichess_cohort_audit,scan_payload
class LichessSelectedRights(unittest.TestCase):
    def fixture(self):
        b={"license":"CC BY-SA 4.0",
           "source_file_SHA256":"a"*64,
           "attribution_original_source":"https://database.lichess.org/broadcast/lichess_db_broadcast_2026-05.pgn.zst"}
        p={"license":"CC0","source_file_SHA256":"b"*64,
           "original_source":"https://database.lichess.org/lichess_db_puzzle.csv.zst"}
        positions=[{"fen4":f"8/8/8/8/8/8/8/{i}K6 w - -","source_root_legal_count":3}
                   for i in range(16)]
        positions2=[{"fen4":f"8/8/8/8/8/8/8/{i}k6 b - -","source_root_legal_count":3}
                    for i in range(16)]
        return {"schema":"c3x023-P1-licensed-independent-May-broadcast-and-disjoint-CC0-nonmate-puzzles-v1",
          "phase":"SOURCE_ONLY__NO_ENGINE_OR_NATIVE_RESULT_YET",
          "source_only_no_stockfish_used":True,
          "per_ecology":{"may2026_broadcast":{"source":b,"selected":positions},
                         "lichess_CC0_nonmate_puzzles":{"source":p,"selected":positions2}}}
    def test_license_status_valid_schema(self):
        self.assertEqual(licensed_lichess_cohort_audit(json.dumps(self.fixture()).encode()),[])
    def test_raw_pgn_header_not_allowlisted(self):
        d=self.fixture()
        d["per_ecology"]["may2026_broadcast"]["selected"][0]["source_headers"]={"White":"Example"}
        self.assertIn("PERSONAL_OR_COMPLETE_GAME_DATA_LEAK",
                      licensed_lichess_cohort_audit(json.dumps(d).encode()))
    def test_source_without_rights_stays_hold(self):
        d=self.fixture()
        d["per_ecology"]["may2026_broadcast"]["source"]["license"]="CC0"
        self.assertIn("LICENCE_DISAGREEMENT",
                      licensed_lichess_cohort_audit(json.dumps(d).encode()))
    def test_p4_does_not_allow_unexamined_zip(self):
        self.assertIn("P4_NON_JSON_SOURCE_NOT_CLEARED",
                     scan_payload("games.zip",b"garbage","P4_LICHESS_LICENSED_SOURCE_ONLY"))
if __name__=="__main__":unittest.main()
