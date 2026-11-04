"""P35/R4 archive-integrity tests. Requires authentic original P34 ZIP paths from CI."""
import json, os, pathlib, tempfile, unittest, zipfile
from c3x_029_p35_r4_archival_lineage_gate import audit, ZIP_SHA

class OriginalArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=("C3X_P35_SOURCE_ZIP","C3X_P35_SEARCH_ZIP","C3X_P35_TRACE_ZIP")
        if any(not os.getenv(n) for n in names):
            raise unittest.SkipTest("Original archived P34 ZIPs not present: no fake fixture PASS")
        cls.source,cls.search,cls.trace=[os.environ[n] for n in names]
    def test_real_originals(self):
        result=audit(self.source,self.search,self.trace)
        self.assertEqual((result["source_games"],result["selected_roots"],result["audited_boards"]),(16,4,12))
        self.assertEqual(result["strict_reversals"],2)
        self.assertEqual({r["root_uci"] for r in result["contrasts"] if r["strict_static_rank_reversal"]},{"e8f7","d5d3"})
        self.assertIn("NOT_NEW_NATIVE_RUN",result["status"])
    def test_trace_bytes_pinned(self):
        import hashlib
        self.assertEqual(hashlib.sha256(pathlib.Path(self.trace).read_bytes()).hexdigest(),ZIP_SHA)
    def test_tampered_trace_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=pathlib.Path(temp)/"altered.zip"
            p.write_bytes(pathlib.Path(self.trace).read_bytes()+b"tampering")
            with self.assertRaisesRegex(ValueError,"RAW_ZIP_SHA"):audit(self.source,self.search,p)
    def test_tampered_source_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=pathlib.Path(temp)/"altered.zip"
            with zipfile.ZipFile(self.source) as original,zipfile.ZipFile(p,"w") as output:
                for name in original.namelist():
                    body=original.read(name)
                    if name=="C3X018_INDEPENDENT_BLIND16_PGN_SOURCE.json":body+=b" "
                    output.writestr(name,body)
            with self.assertRaisesRegex(ValueError,"SHA_"):audit(p,self.search,self.trace)
if __name__=="__main__":unittest.main()
