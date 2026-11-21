"""0.31/P2 source admission tests; synthetic games are NOT chess observations."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import chess.pgn

from c3x_031_p2_source_intake import (
    BLOCKLIST_SHA, CAP, check_blocklist, digest, make_p2_cohort,
)

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED=ROOT/"frozen/C3X_031_P2_PRIOR_USED_EVENT_FAMILIES_20261121.txt"


def pgn_case(event, first):
    g=chess.pgn.Game()
    g.headers["Event"]=event
    g.headers["White"]="Synthetic"
    g.headers["Black"]="Synthetic"
    g.add_variation(g.board().parse_uci(first))
    return str(g)+"\n\n"


class SourceIntakeTests(unittest.TestCase):
    def test_real_exclusion_file_matches_original_sha(self):
        self.assertEqual(digest(EXCLUDED.read_bytes()),BLOCKLIST_SHA)
        names=check_blocklist(EXCLUDED)
        self.assertEqual(len(names),94)
        for required in ("34th ey open u14 2026","tournament of peace 2026",
                         "semifinals ch-pol 2026","sixdays budapest sept ima"):
            self.assertIn(required,names)

    def test_source_audit_starts_with_zip_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.zip"
            path.write_text("not a ZIP")
            with self.assertRaises(Exception):
                make_p2_cohort(path,EXCLUDED)

    def test_exclusion_file_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"changed.txt"
            path.write_bytes(EXCLUDED.read_bytes()+b"new family\n")
            with self.assertRaises(ValueError):
                check_blocklist(path)

    def test_synthetic_legal_pgn_freezes_unseen_case_and_excludes_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"twic1669g.zip"
            data=(pgn_case("17th China Danzhou","e2e4")+
                  pgn_case("UNSEEN SYNTHETIC P2 EVENT","d2d4")+
                  pgn_case("SECOND NOVEL EVENT","c2c4")).encode("latin-1")
            with ZipFile(path,"w") as zip:
                zip.writestr("twic1669.pgn",data)
            from c3x_031_p2_source_intake import PUBLISHER_GAMES
            with patch("c3x_031_p2_source_intake.PUBLISHER_GAMES",3), \
                 patch("c3x_031_p2_source_intake.CHECKPOINTS",(1,)):
                result=make_p2_cohort(path,EXCLUDED)
            self.assertEqual(result["parsed_games"],3)
            self.assertEqual(result["source_native_treatments_seen"],0)
            self.assertEqual(result["counts"]["historical_family_excluded"],1)
            self.assertEqual(result["preselected_games"],2)
            self.assertEqual(result["preselected_unique_families"],2)
            self.assertEqual(len({r["game_sha256"] for r in result["positions"]}),2)
            self.assertTrue(all(len(r["moves"])==1 for r in result["positions"]))

    def test_wrong_issue_member_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"fake.zip"
            with ZipFile(path,"w") as zip:
                zip.writestr("twic1670.pgn",pgn_case("NEW","e2e4"))
            with self.assertRaises(ValueError):
                make_p2_cohort(path,EXCLUDED)


if __name__=="__main__":
    unittest.main()
