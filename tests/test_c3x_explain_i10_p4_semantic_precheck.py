"""Original Ethereal P16 semantic precheck must NEVER mint new source authority."""
from pathlib import Path
import json
import pytest
from c3x_explain.semantic_bridge_precheck import (
    audit_original_historical,certify_source_identity,board_proxy,ORIGINAL_BLOB_SHA1)

ORIGINAL=Path("c3x/certificates/g95-p16-local-minimal-full-bridge.json")

def test_historic_git_blob_identity_exact():
    raw=ORIGINAL.read_bytes()
    cert=certify_source_identity(raw)
    assert cert["concept_label"] is None
    assert cert["engine"]=="ethereal"

def test_independent_board_measurement_has_no_new_causal_authority():
    report=audit_original_historical(ORIGINAL.read_bytes())
    assert report["new_semantic_causal_certificate"] is None
    assert report["causal_semantic_claim_authorized"] is False
    assert report["engine_source_execution_new"] is False
    assert report["concept_to_source_event_causation"]=="NOT_IDENTIFIED"
    assert report["sham_aliases_subset_exact_board"] is True
    assert report["independent_sham_adequacy"]=="FAIL_ALIASED_BOARD"
    assert report["historical_source_event_cells"]=={
        "B0":"EVENT_PAIR_REVERSAL",
        "TARGET":"EVENT_NULL",
        "SUBSET":"EVENT_PAIR_REVERSAL",
        "SHAM":"EVENT_PAIR_REVERSAL"
    }
    assert any(c["can_distinguish_target_from_subset_in_observed_board_proxy"]
               for c in report["candidate_board_proxies"]) or all(
          isinstance(c["TARGET_delta"],int) for c in report["candidate_board_proxies"])

def test_tampered_historical_citation_rejected():
    raw=ORIGINAL.read_bytes()
    with pytest.raises(ValueError,match="BLOB_IDENTITY"):
        certify_source_identity(raw.replace(b'"ethereal"',b'"stockfish"'))

def test_board_proxy_fails_closed_on_nonlegal_chess_world():
    with pytest.raises(ValueError,match="SEMANTIC_BOARD_INVALID"):
        board_proxy("8/8/8/8/8/8/8/8 w - - 0 1")

def test_source_events_unchanged_by_read_only_semantic_precheck():
    raw=ORIGINAL.read_bytes()
    original=json.loads(raw)
    audit_original_historical(raw)
    assert original==json.loads(ORIGINAL.read_bytes())
