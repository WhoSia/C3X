"""Synthetic-only trust-admission regression, no C3X scientific outcome."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"c3x_explain"/"certificate_trust.py"
spec=importlib.util.spec_from_file_location("c3x_012_trust_test_module",SCRIPT)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CausalAdmissionTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir=Path(self.temp.name)
        self.cert=self.dir/"certificate.json"
        self.trust=self.dir/"trusted.json"
        self.payload={"schema":"test-fixture-only","certificate_id":"not-real",
                      "scientific_stage":"C3X SYNTHETIC TEST","pair":"e2e4::d2d4","bound":"LOWER"}
        self.cert.write_text(json.dumps(self.payload),encoding="utf-8")
        self.digest=hashlib.sha256(self.cert.read_bytes()).hexdigest()
        self.allow={"sha256":self.digest,"certificate_ids":["not-real"],
                    "scientific_stage":"C3X SYNTHETIC TEST",
                    "review_receipt_sha256":"a"*64,
                    "status":m.APPROVED}
    def manifest(self,entries):
        self.trust.write_text(json.dumps({"schema":m.SCHEMA,"approved":entries}),encoding="utf-8")
    def test_default_no_certificates(self):
        self.assertEqual(m.admitted_certificates([]),[])
    def test_unlisted_file_fails_closed(self):
        self.manifest([])
        with self.assertRaisesRegex(ValueError,"UNREVIEWED_CAUSAL_CERTIFICATE_FILE"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_test_fixture_admission_only_when_exact_hash_reviewed(self):
        self.manifest([self.allow])
        self.assertEqual(m.admitted_certificates([str(self.cert)],self.trust),[self.payload])
    def test_mutation_after_review_fails(self):
        self.manifest([self.allow])
        self.cert.write_text(json.dumps({**self.payload,"bound":"UPPER"}))
        with self.assertRaisesRegex(ValueError,"UNREVIEWED_CAUSAL_CERTIFICATE_FILE"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_wrong_identity_fails(self):
        self.allow["certificate_ids"]=["other"]
        self.manifest([self.allow])
        with self.assertRaisesRegex(ValueError,"CAUSAL_CERTIFICATE_MANIFEST_IDENTITY_MISMATCH"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_wrong_stage_fails(self):
        self.allow["scientific_stage"]="C3X 0.12"
        self.manifest([self.allow])
        with self.assertRaisesRegex(ValueError,"CAUSAL_CERTIFICATE_MANIFEST_IDENTITY_MISMATCH"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_missing_receipt_fails(self):
        del self.allow["review_receipt_sha256"]
        self.manifest([self.allow])
        with self.assertRaisesRegex(ValueError,"INVALID_CAUSAL_TRUST_ENTRY"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_duplicate_digest_fails(self):
        self.manifest([self.allow,self.allow])
        with self.assertRaisesRegex(ValueError,"INVALID_CAUSAL_TRUST_ENTRY"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_invalid_manifest_fails(self):
        self.trust.write_text('{"schema":"wrong","approved":[]}')
        with self.assertRaisesRegex(ValueError,"INVALID_CAUSAL_TRUST_MANIFEST"):
            m.admitted_certificates([str(self.cert)],self.trust)
    def test_missing_identity_fails(self):
        self.cert.write_text(json.dumps({k:v for k,v in self.payload.items() if k!="certificate_id"}))
        self.allow["sha256"]=hashlib.sha256(self.cert.read_bytes()).hexdigest()
        self.manifest([self.allow])
        with self.assertRaisesRegex(ValueError,"CAUSAL_CERTIFICATE_MANIFEST_IDENTITY_MISMATCH"):
            m.admitted_certificates([str(self.cert)],self.trust)

if __name__=="__main__":
    unittest.main()
