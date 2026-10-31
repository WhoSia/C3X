import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p20_archive_chess_cohort_census import census
F=Path(__file__).resolve().parents[1]/"c3x/cohorts/c3x-016-P4-Lichess-12-standalone-FEN-source-geometry-3x4-preoutcome.json"
class Archive(unittest.TestCase):
 def test_actual_archive_admitted_only_as_history_census(self):
  a=census(json.loads(F.read_text()))
  self.assertEqual(a["status"],"ARCHIVE_CENSUS_PASS_BENCHMARK_ADMISSION_HOLD")
  self.assertEqual(a["cases"],12)
  self.assertEqual(set(a["strata"].values()),{3})
 def test_removed_case_refused(self):
  d=json.loads(F.read_text());d["cases"].pop()
  self.assertEqual(census(d)["status"],"FAIL_COHORT_CARDINALITY")
 def test_four_field_source_scope(self):
  d=json.loads(F.read_text());d["cases"][0]["fen"]+=" 0 1"
  self.assertEqual(census(d)["status"],"FAIL_EXPECTED_FOUR_FIELD_FEN")
if __name__=="__main__":unittest.main()
