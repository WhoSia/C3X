"""Read-only, research-only audit of the original C3X G9.5-P16 Ethereal chess certificate.

Explicitly NOT a public I9/I10 causal-admission bypass, NOT Stockfish
causal evidence, NOT fresh re-execution of G9.5 native source experiments.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import chess

SCHEMA = "c3x-explain-i10-p2-original-p16-scoped-certificate-interpretation-v1"
P16 = Path("c3x/certificates/g95-p16-local-minimal-full-bridge.json")
TRUST = Path("c3x/ontology/c3x-012-causal-certificate-trust.json")
OLD_GIT_BLOB_SHA1 = "53765418975095ec5981da35464859e01f030902"
CERT_ID = "398eca8d6adf00525e6d5bf7"
EXPECTED_ENGINE="ethereal"
FEN_B0="r1bqk2r/pp2bppp/2nppn2/8/2PP4/2N2NP1/PP3PBP/R1BQK2R b KQkq - 0 1"
EXPECTED_PAIR=("d6d5","e8g8")

def audit_original(c:dict, trust:dict, *, original_blob:bytes, check_git_blob:bool=True)->dict:
    if check_git_blob:
        # The stored official historical Git object ID was read through GitHub,
        # and protects our audit against silently substituting a new local witness.
        header=f"blob {len(original_blob)}\\0".encode()
        git_hash=hashlib.sha1(header+original_blob).hexdigest()
        if git_hash!=OLD_GIT_BLOB_SHA1:
            raise ValueError("ORIGINAL_SOURCE_BYTE_IDENTITY_MISMATCH")
    if (c.get("schema")!="c3x-causal-contrast-certificate-v1"
        or c.get("certificate_id")!=CERT_ID
        or c.get("engine")!=EXPECTED_ENGINE
        or c.get("replication_status")!="LOCAL_ONLY"
        or c.get("scientific_stage")!="C3X 0.7.0-G9.5-P16"
        or c.get("scientific_verdict")!="P16_LOCAL_MINIMAL_FULL_BRIDGE_ONLY"):
        raise ValueError("SCOPED_ENGINE_OR_CERTIFICATE_IDENTITY_MISMATCH")
    pair=c["pair"]
    if (pair.get("pair_id")!="d6d5::e8g8"
        or (pair["A"]["uci"],pair["B"]["uci"])!=EXPECTED_PAIR):
        raise ValueError("RIVAL_PAIR_IDENTITY_MISMATCH")
    if c["counterfactual_boards"]["B0"]["fen"]!=FEN_B0:
        raise ValueError("B0_CHESS_WORLD_MISMATCH")
    b0=chess.Board(FEN_B0)
    if not b0.is_valid():
        raise ValueError("B0_NOT_VALID_CHESS_WORLD")
    moves=[chess.Move.from_uci(x) for x in EXPECTED_PAIR]
    if any(m not in b0.legal_moves for m in moves):
        raise ValueError("REPORTED_SOURCE_RIVAL_NOT_LEGAL_IN_B0")
    for name,blob in c["counterfactual_boards"].items():
        b=chess.Board(blob["fen"])
        if not b.is_valid():raise ValueError("COUNTERFACTUAL_WORLD_NOT_VALID:"+name)
    chain=c["chain"]
    if (chain.get("bound")!="LOWER"
        or chain.get("chain_id")!="d8c7::SHAM::d8d7"
        or chain["target_edit"]["from"]!="d8"
        or chain["target_edit"]["to"]!="c7"
        or chain["subset_edit"]["to"]!="d7"):
        raise ValueError("INTERVENTION_EDIT_FAMILY_MISMATCH")
    cells=c["decision_cells"]
    for n,move,state in (
        ("B0","d6d5","EVENT_PAIR_REVERSAL"),
        ("TARGET","e8g8","EVENT_NULL"),
        ("SUBSET","e8g8","EVENT_PAIR_REVERSAL"),
        ("SHAM","e8g8","EVENT_PAIR_REVERSAL"),
    ):
        if (cells[n]["native_bestmove"]!=move or
            cells[n]["bounds"]["LOWER"]["state"]!=state):
            raise ValueError("ENGINE_EVENT_RESPONSE_CELL_MISMATCH:"+n)
    if (c["counterfactual_boards"]["SUBSET"]["fen"] !=
        c["counterfactual_boards"]["SHAM"]["fen"]):
        raise ValueError("SHAM_CONTROLS_INCONSISTENT")
    if (trust.get("schema")!="c3x-012-causal-certificate-trust-manifest-v1"
        or trust.get("approved")!=[]):
        raise ValueError("USER_FACING_TRUST_POLICY_UNEXPECTED")
    replay_san=[b0.san(move) for move in moves]
    return {
        "schema":SCHEMA,
        "historical_git_blob_sha1":OLD_GIT_BLOB_SHA1,
        "source_bytes_sha256":hashlib.sha256(original_blob).hexdigest(),
        "original_science_stage":"C3X 0.7.0-G9.5-P16",
        "original_legacy_certificate_id":CERT_ID,
        "original_engine":"Ethereal",
        "original_engine_executed_during_THIS_P2_court":False,
        "source_authority":"PRIOR_LOCAL_ONLY_REVIEWED_HISTORICAL_RESEARCH_CERTIFICATE",
        "source_reproduction_this_run":"NOT_REEXECUTED",
        "user_facing_I9_I10_trust_status":"NOT_PUBLICLY_ADMITTED",
        "public_trust_approved_entry_count":0,
        "stockfish_source_causal_authority":"NONE",
        "chess_concept_semantic_validation":"NOT_PERFORMED_CONCEPT_LABEL_NULL",
        "chess_world_FEN_B0":FEN_B0,
        "root_pair":[{"uci":move.uci(),"san":san,"legal":True}
                     for move,san in zip(moves,replay_san)],
        "actual_original_certificate_observation":{
            name:{
                "native_bestmove":cells[name]["native_bestmove"],
                "source_lower_event_state":cells[name]["bounds"]["LOWER"]["state"],
                "recorded_native_source_only_not_fresh":True
            } for name in ["B0","TARGET","SUBSET","SHAM"]
        },
        "difference_not_to_conflate":[
            "B0->TARGET: both source event and original recorded move preference differ",
            "B0->SUBSET: recorded original move preference differs, yet LOWER source event remains EVENT_PAIR_REVERSAL",
            "TARGET->SUBSET: original root recommendation identical e8g8, but source-event result differs",
            "This cannot establish universal cause, exact human chess strategy, objective best chess move or human understanding"
        ],
        "human_readable_chess_contrast_ko":(
            "원래 검증된 흑 차례 국면에서는 역사적 Ethereal 엔진 기록상 d5가 O-O보다 선택됐습니다. "
            "퀸을 d8에서 c7로 옮긴 정해진 비교 세계에서는 O-O로 선택이 바뀌었습니다. "
            "퀸을 d7로 옮긴 대조 세계도 O-O를 선택하지만, 소스 LOWER 이벤트의 반응 서명은 서로 다릅니다. "
            "이는 기존 원본 계산 기록의 한정된 국소 인과 증거이며, "
            "‘왜 캐슬링이 체스적으로 최선인가’를 증명하거나 Stockfish 원인을 설명하지 않습니다."
        ),
        "generic_public_Stockfish_commentator_would_be_unauthorized":True,
        "human_utility_score":None,
        "new_C3X_P2_independent_scientific_contribution":False,
        "methodological_use":"Evidence-vs-narration boundary, exact engine-specific causal-language refusal and future strong-rival evaluation source",
    }

def produce()->dict:
    data=P16.read_bytes()
    cert=json.loads(data)
    trust=json.loads(TRUST.read_text(encoding="utf-8"))
    return audit_original(cert,trust,original_blob=data)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    result=produce()
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("I10_P2_P16_CERT_AUTHENTIC_SOURCE_RESEARCH_ONLY",result["original_legacy_certificate_id"],
          result["source_authority"],result["user_facing_I9_I10_trust_status"],
          result["root_pair"])

if __name__=="__main__":main()
