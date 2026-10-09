import unittest
from c3x017_depth8_semantic_source_audit import cls
class RootEvidenceTest(unittest.TestCase):
 def base(self):
  return {"kind":"candidate","depth":8,"move":1380,"index":4,"alpha":130,"beta":162,"child_return":14,"before":-32001,"after":-32001}
 def test_child_only(self):
  a=self.base();b={**a,"child_return":130};self.assertEqual(cls(a,b),"CHILD_RETURN_DIFFERENT")
 def test_store_only(self):
  a=self.base();b={**a,"after":14};self.assertEqual(cls(a,b),"ROOT_SCORE_STORAGE_DIFFERENT")
 def test_window_first(self):
  a=self.base();b={**a,"alpha":131,"child_return":130};self.assertEqual(cls(a,b),"ALPHA_BETA_WINDOW_DIFFERENT")
 def test_move_alignment(self):
  a=self.base();b={**a,"move":999};self.assertEqual(cls(a,b),"EVENT_ALIGNMENT_AMBIGUOUS_CANDIDATE")
 def test_depth_alignment(self):
  a=self.base();b={**a,"depth":9};self.assertEqual(cls(a,b),"EVENT_ALIGNMENT_AMBIGUOUS_KIND_DEPTH")
 def test_identical(self):
  a=self.base();self.assertIsNone(cls(a,{**a,"root_nodes":100}))
if __name__=="__main__":unittest.main()
