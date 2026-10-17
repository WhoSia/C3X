import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "crates/c3x-evidence-automata/dev_fixture.json"
MANIFEST = ROOT / "crates/c3x-evidence-automata/Cargo.toml"
ADAPTER = ROOT / "tools/i10_p8_native_trace_adapter.py"


class NativeRustInterop(unittest.TestCase):
    def test_end_to_end_and_authority_ceiling(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        raw = ("\n".join(fixture["lines"]) + "\n").encode("utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            log = d / "synthetic.log"
            envelope = d / "input.json"
            receipt = d / "receipt.json"
            verdict_path = d / "verdict.json"

            log.write_bytes(raw)

            subprocess.run([
                sys.executable, str(ADAPTER),
                "--raw", str(log),
                "--run-id", "interop-synthetic",
                "--output-json", str(envelope),
                "--output-receipt", str(receipt),
            ], check=True, capture_output=True, text=True)

            subprocess.run([
                "cargo", "run", "--quiet", "--locked",
                "--manifest-path", str(MANIFEST),
                "--", str(envelope), str(verdict_path),
            ], check=True, capture_output=True, text=True)

            custody = json.loads(receipt.read_text())
            ingested = json.loads(envelope.read_text())
            verdict = json.loads(verdict_path.read_text())

            self.assertEqual(
                custody["raw_sha256"], hashlib.sha256(raw).hexdigest()
            )
            self.assertEqual(ingested["lines"], fixture["lines"])
            self.assertEqual(verdict["joined_triples"], 1)
            self.assertEqual(
                verdict["evidence_level"], "STRUCTURAL_CHAIN_OBSERVED"
            )
            self.assertEqual(
                verdict["source_authentication"],
                "EXTERNAL_BYTE_AND_SOURCE_ATTESTATION_REQUIRED"
            )
            self.assertIn(
                "NATURAL_TT_SEE_ROOT_MEDIATION",
                verdict["prohibited_claims"],
            )
            self.assertIn(
                "C3X_0_26_PROMOTION",
                verdict["prohibited_claims"],
            )


if __name__ == "__main__":
    unittest.main()
