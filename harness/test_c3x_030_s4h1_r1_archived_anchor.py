import unittest
from c3x_030_s4h1_r1_archived_anchor import attest, H0_MANIFEST_SHA256

class TestArchivedAnchor(unittest.TestCase):
    def test_wrong_original_rejected(self):
        with self.assertRaisesRegex(ValueError, "ARCHIVED_H0"):
            attest(b'{}', b'{}')
    def test_new_manifest_cannot_self_certify(self):
        with self.assertRaisesRegex(ValueError, "ARCHIVED_H0"):
            attest(b'{"schema":"x"}', b'{"schema":"x"}')
    def test_reference_is_64_digit_lowercase_sha(self):
        self.assertEqual(len(H0_MANIFEST_SHA256), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in H0_MANIFEST_SHA256))
    def test_a_bad_reproduction_cannot_override_original(self):
        with self.assertRaisesRegex(ValueError, "ARCHIVED_H0"):
            attest(b'original', b'altered')
if __name__ == "__main__": unittest.main()
