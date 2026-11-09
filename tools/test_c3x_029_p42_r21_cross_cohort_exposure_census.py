"""R21 C historical census tests: no fictitious heldout closure."""
import unittest
import chess
from c3x_029_p42_r21_cross_cohort_exposure_census import compare

def fixture():
    sep={"phase":"SOURCE_ONLY_PRE_NATIVE_TREATMENT",
         "source_games":[{"source_game_sha256":f"{i:064x}","fen4":f"fake-fen-{i}"} for i in range(1,17)]}
    src=[]
    for i in range(8):
        board=chess.Board()
        for u in ["e2e4","e7e5"]*15:
            # This sequence is NOT legal; use a legal alternate repeated knight dance.
            pass
        board=chess.Board()
        moves=(["g1f3","g8f6","f3g1","f6g8"]*8)[:30]
        for u in moves:board.push_uci(u)
        src.append({"source_id":f"event-{i}","selected":{
            "full_game_uci_sha256":f"{i+100:064x}",
            "fixed_ply":30,"full_game_uci":moves,
            "frozen_fen":board.fen(en_passant="fen")}})
    return sep,{"sources":src}

class SourceCohortCensus(unittest.TestCase):
    def test_exact_duplicate_FEN_across_samples_is_not_hidden(self):
        a,b=fixture();a["source_games"][0]["fen4"]=" ".join(
            b["sources"][0]["selected"]["frozen_fen"].split()[:4])
        z=compare(a,b);self.assertEqual(z["exact_chess_fen4_intersection_count"],1)
        self.assertFalse(z["fresh_prospective_cohort"])
    def test_no_original_case_removed(self):
        a,b=fixture();r=compare(a,b)
        self.assertEqual(r["source_sept16_case_count"],16)
        self.assertEqual(r["source_oct8_game_count"],8)
    def test_duplicate_original_game_hash_rejected(self):
        a,b=fixture();a["source_games"][0]["source_game_sha256"]=a["source_games"][1]["source_game_sha256"]
        with self.assertRaisesRegex(ValueError,"SEPT_GAME_DUPLICATE"):compare(a,b)
    def test_duplicate_event_rejected(self):
        a,b=fixture();b["sources"][0]["source_id"]="event-1"
        with self.assertRaisesRegex(ValueError,"SOURCE_EVENT_DUPLICATE"):compare(a,b)
    def test_oct_history_mismatch_rejected(self):
        a,b=fixture();b["sources"][0]["selected"]["frozen_fen"]=chess.STARTING_FEN
        with self.assertRaisesRegex(ValueError,"FEN_REPLAY_MISMATCH"):compare(a,b)
    def test_oct_illegal_original_history_rejected(self):
        a,b=fixture();b["sources"][0]["selected"]["full_game_uci"][0]="e2e5"
        with self.assertRaisesRegex(ValueError,"ILLEGAL_OCT_HISTORY"):compare(a,b)
    def test_missing_one_case_holds(self):
        a,b=fixture();b["sources"].pop()
        with self.assertRaisesRegex(ValueError,"SOURCE_CASE_COUNT"):compare(a,b)
    def test_novelty_overclaim_is_never_generated(self):
        a,b=fixture();r=compare(a,b)
        self.assertFalse(r["full_prior_archive_exclusion_proved"])
        self.assertFalse(r["source_game_hash_algorithms_equivalent_proved"])
        self.assertFalse(r["novel_chess_value_evidence"])

if __name__=="__main__":
    unittest.main()
