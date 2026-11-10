#!/usr/bin/env python3
"""C3X 0.30/R6-A: REAL pinned open-weight tiny decoder on R5 blind arms.

Original paper (owned Drive): Angelina Parfenova (2026) 2609.22245v1.
This is a behavioral protocol pilot, NOT the original 200 Lichess puzzles,
GPT/Llama/Qwen3 decoder benchmark, token scoring or generated/reference split.

The decoder process accepts ONLY one isolated R5 arm file per invocation,
NEVER the truth/audit file. Its prompt contains only FEN and explanation.
Outputs have arm + ordinal + raw prediction, no case IDs/target. Evaluate
separately in another process AFTER all arm predictions have been sealed.

Model Qwen/Qwen2.5-0.5B-Instruct is open Apache-2.0 but much smaller than
the Qwen3-32B in the primary paper. Revision is immutable pinned SHA.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

MODEL_ID="Qwen/Qwen2.5-0.5B-Instruct"
MODEL_REVISION="7ae557604adf67be50417f59c2c2f167def9a775"
SCHEMA="c3x030-r6-actual-small-open-decoder-v1"
R5_SCHEMA="c3x030-r5-decoder-only-arm-input-v1"
ARMS=("fen_only","explanation_only","fen_plus_unmasked",
      "fen_plus_strict_masked","fen_plus_unrelated_foil")
# Strict UCI: no extracting moves mentioned later in generated prose.
UCIOUT=re.compile(r"^\s*(?:\x60)?(?:Best move(?: in UCI)?\s*:\s*)?([a-h][1-8][a-h][1-8][qrbn]?)(?![A-Za-z0-9])",re.I)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prompt_for(entry):
    if not isinstance(entry,dict) or set(entry)!={"fen","explanation"}:
        raise ValueError("R030_R6_HOLD_NONBLIND_DECODER_FIELDS")
    fen,exp=entry["fen"],entry["explanation"]
    if fen is not None and (type(fen) is not str or not fen.strip()):
        raise ValueError("R030_R6_HOLD_FEN_TYPE")
    if exp is not None and (type(exp) is not str or not exp.strip()):
        raise ValueError("R030_R6_HOLD_EXPLANATION_TYPE")
    if fen is None and exp is None:
        raise ValueError("R030_R6_HOLD_NO_CONDITION_INPUT")
    parts=["You are evaluating a chess position. Output exactly one UCI move (e.g. e2e4), no explanation."]
    if fen is not None:
        parts.append("Position (FEN): "+fen)
    if exp is not None:
        parts.append("Explanation: "+exp)
    parts.append("Best move in UCI:")
    return "\n".join(parts)


def input_arm(data,arm):
    if (not isinstance(data,dict) or data.get("schema")!=R5_SCHEMA
        or data.get("condition")!=arm or arm not in ARMS
        or data.get("no_target_labels_or_cross_arm_case_identifiers") is not True
        or data.get("requires_isolated_decoder_context_no_cross_arm_visibility") is not True
        or set(data)!={"schema","condition","entries",
                        "no_target_labels_or_cross_arm_case_identifiers",
                        "requires_isolated_decoder_context_no_cross_arm_visibility",
                        "no_decoder_executed"}
        or not isinstance(data["entries"],list) or len(data["entries"])!=4):
        raise ValueError("R030_R6_HOLD_R5_ARM_PROVENANCE_OR_TARGET_LEAK")
    for e in data["entries"]:
        prompt_for(e)
    return data["entries"]



def read_legacy_r5_blind(path):
    """Exact historical R5 artifact had a literal two-byte backslash+n tail.

    This is ONLY for SHA-pinned R5 legacy files. Never normalize arbitrary
    invalid JSON: the CI must verify known whole-file SHA first. Record
    normalization in resulting decoder metadata.
    """
    raw=Path(path).read_bytes()
    if not raw.endswith(bytes([92,110])):
        raise ValueError("R030_R6_HOLD_EXPECTED_PINNED_R5_LITERAL_BACKSLASH_N")
    clean=raw[:-2]
    return json.loads(clean.decode("utf-8"))


def parse_strict_uci(response):
    if type(response) is not str:
        raise ValueError("R030_R6_HOLD_NONSTRING_MODEL_RESPONSE")
    m=UCIOUT.match(response)
    return m.group(1).lower() if m else None


def run(arm,arm_file,model,tokenizer,torch):
    data=read_legacy_r5_blind(arm_file)
    entries=input_arm(data,arm)
    results=[]
    for index,entry in enumerate(entries):
        # Each request uses a FRESH prompt/kv cache, not shared chat history.
        messages=[{"role":"system","content":"Only output a legal chess move in UCI format. Answer with the UCI code alone."},
                  {"role":"user","content":prompt_for(entry)}]
        input_ids=tokenizer.apply_chat_template(messages,return_tensors="pt",
                                                 add_generation_prompt=True)
        with torch.inference_mode():
            generated=model.generate(input_ids,do_sample=False,
                                     max_new_tokens=12,pad_token_id=tokenizer.eos_token_id)
        decoded=tokenizer.decode(generated[0,input_ids.shape[-1]:],
                                 skip_special_tokens=True).strip()
        pred=parse_strict_uci(decoded)
        results.append({"ordinal":index,"raw_generated_text":decoded[:400],
                        "parsed_uci_or_null":pred,
                        "decoder_input_tokens":int(input_ids.shape[-1]),
                        "no_original_target_used_by_decoder":True})
        print("R030_R6_DECODER_ARM",arm,index,repr(pred),flush=True)
    return {
        "schema":SCHEMA,"arm":arm,
        "model_id":MODEL_ID,"model_revision":MODEL_REVISION,
        "input_blind_arm_sha256":digest(arm_file),
        "normalized_only_legacy_r5_literal_backslash_n_after_sha_verification":True,
        "greedy_generation_max_new_tokens":12,
        "isolated_chat_context_every_entry":True,
        "no_truth_manifest_access_in_decoder":True,
        "not_original_paper_200_puzzle_protocol":True,
        "not_original_Qwen3_32B_model":True,
        "results":results,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("arm","input","out"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    if a.arm not in ARMS:
        raise ValueError("R030_R6_HOLD_UNKNOWN_ARM")
    # Verify R5 arm completely BEFORE any model download.
    data=read_legacy_r5_blind(a.input)
    input_arm(data,a.arm)
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2)
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,revision=MODEL_REVISION,
                                             trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(
        MODEL_ID,revision=MODEL_REVISION,trust_remote_code=False,
        torch_dtype=torch.float32,low_cpu_mem_usage=True)
    model.eval()
    report=run(a.arm,a.input,model,tokenizer,torch)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("R030_R6_DECODER_ACTUAL_COMPLETE",a.arm,digest(out),flush=True)


if __name__=="__main__":
    main()
