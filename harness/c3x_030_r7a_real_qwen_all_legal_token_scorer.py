#!/usr/bin/env python3
"""C3X 0.30/R7-A: actual pinned Qwen teacher-forced all-legal move ranking.

Primary owned Parfenova (2026) original PDF:
https://drive.google.com/file/d/1pNg13f4_OII1N1GUThSwB8I5ru_3Ns_R/view

The model reads ONE R5 blind arm, and a legal UCI candidate-support list
derived SOLELY from a separate R5 FEN-only BLIND arm (no historical target).
It never reads the R5 audit with nominated targets or original gold labels.

Score every legal action u by:
  sum_j log P_theta(token_j | chat_prompt, preceding candidate tokens)
where continuation tokenizer is applied to precisely " "+u. Prompt is
IDENTICAL to R6's actual generation prompt, same immutable model revision.
A second per-token average is merely a secondary length-bias sensitivity
analysis, not a comparable log-probability of full strings. Fixed prompt,
chosen candidate tokenization convention, ties UCI lexicographic.

To avoid CPU repeated prompt computation, compute prefix with KV cache
once per entry; then teacher-force candidate tokens using isolated
copies of that immutable prefix. We reject non-finite score, length<1,
and any drift in legal support/cardinality. No model-generated move from
Parfenova's original puzzle study, no true gold puzzle reference.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from c3x_030_r6a_actual_open_decoder_blind_arm import (
    ARMS,MODEL_ID,MODEL_REVISION,read_legacy_r5_blind,input_arm,prompt_for
)
from c3x_030_r7s_blind_all_legal_support_freeze import (
    SCHEMA as SUPPORT_SCHEMA,FEN_SHA
)

SCHEMA="c3x030-r7a-real-qwen-complete-legal-uci-loglik-v1"
MAX_ACTIONS=220


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_arm_and_support(arm_data,arm,support_data):
    examples=input_arm(arm_data,arm)
    if (support_data.get("schema")!=SUPPORT_SCHEMA
        or support_data.get("source_fen_only_blind_sha256")!=FEN_SHA
        or support_data.get("no_fen_or_reference_label_in_support_manifest") is not True
        or set(support_data)!={"schema","source_fen_only_blind_sha256",
          "no_fen_or_reference_label_in_support_manifest",
          "source_not_generated_or_reference_move_labels",
          "same_board_can_appear_in_multiple_original_ordinal_rows",
          "requires_original_ordinal_alignment_across_isolated_arms","entries"}
        or support_data.get("source_not_generated_or_reference_move_labels") is not True
        or len(support_data.get("entries",[]))!=4):
        raise ValueError("R030_R7_HOLD_BLIND_LEGAL_SUPPORT_PROVENANCE")
    seen=[]
    for i,(entry,item) in enumerate(zip(examples,support_data["entries"])):
        if type(item) is not dict or set(item)!={"ordinal","legal_move_ucis"} or item["ordinal"]!=i:
            raise ValueError("R030_R7_HOLD_SUPPORT_ORDINAL")
        actions=item["legal_move_ucis"]
        if (type(actions) is not list or not 3<=len(actions)<=MAX_ACTIONS
            or not all(type(u) is str and len(u) in (4,5) and
                       u[:4].isalnum() for u in actions)
            or actions != sorted(set(actions))):
            raise ValueError("R030_R7_HOLD_SORTED_EXACT_LEGAL_SUPPORT")
        if entry["fen"] is not None:
            import chess
            board=chess.Board(entry["fen"])
            if not board.is_valid() or sorted(m.uci() for m in board.legal_moves)!=actions:
                raise ValueError("R030_R7_HOLD_BOARD_ACTION_DRIFT")
        seen.append(actions)
    return examples,seen


def token_suffix(tokenizer,move):
    # EXACT ex-ante decision: scoring the convention of a single SPACED UCI
    # continuation, without EOS, with tokenizer.encode(..., add_special_tokens=False).
    ids=tokenizer.encode(" "+move,add_special_tokens=False)
    if (not isinstance(ids,list) or not 1<=len(ids)<=12
        or any(type(t) is not int or t<0 for t in ids)):
        raise ValueError("R030_R7_HOLD_UCI_TOKENIZATION")
    return ids


def choose_ranking(scored,metric="summed_log_probability"):
    if not isinstance(scored,list) or not scored:
        raise ValueError("R030_R7_HOLD_EMPTY_SCORE_LIST")
    if len(set(x["uci"] for x in scored))!=len(scored):
        raise ValueError("R030_R7_HOLD_DUPLICATE_UCI_IN_RANKING")
    for x in scored:
        if (not math.isfinite(x[metric])
            or type(x.get("continuation_tokens")) is not int
            or x["continuation_tokens"]<1):
            raise ValueError("R030_R7_HOLD_NONFINITE_OR_MISSING_SCORE")
    return sorted(scored,key=lambda x:(-x[metric],x["uci"]))


def score_all_moves(input_ids,uci_actions,tokenizer,model,torch):
    """One source prompt forward, then teacher-force every legal UCI continuation.

    Prefix cache returned by an HF model might be a mutable DynamicCache.
    Its per-action clone is needed to avoid cross-candidate hidden state
    carry-over. Tied to R6's pinned tokenizer and model.
    """
    import copy
    if input_ids.ndim!=2 or input_ids.shape[0]!=1:
        raise ValueError("R030_R7_HOLD_SINGLE_PROMPT_SHAPE")
    with torch.inference_mode():
        prefix=model(input_ids=input_ids,use_cache=True,return_dict=True)
        first_logp=torch.log_softmax(prefix.logits[0,-1,:].float(),dim=-1)
        scored=[]
        for u in uci_actions:
            tokens=token_suffix(tokenizer,u)
            first=float(first_logp[tokens[0]])
            total=first
            if len(tokens)>1:
                prev=torch.tensor([tokens[:-1]],dtype=torch.long,device=input_ids.device)
                # Build fresh independent cached prefix for this candidate.
                # qwen2 model in transformers 4.47 returns DynamicCache; deepcopy
                # prevents later action continuations from modifying original.
                candidate_cache=copy.deepcopy(prefix.past_key_values)
                mask=torch.ones((1,input_ids.shape[1]+len(tokens)-1),
                                dtype=torch.long,device=input_ids.device)
                continuation=model(input_ids=prev,attention_mask=mask,
                                  past_key_values=candidate_cache,
                                  use_cache=False,return_dict=True)
                rows=torch.log_softmax(continuation.logits[0].float(),dim=-1)
                if rows.shape[0]!=len(tokens)-1:
                    raise ValueError("R030_R7_HOLD_CONTINUATION_LOGIT_ALIGNMENT")
                for j,tok in enumerate(tokens[1:]):
                    total+=float(rows[j,tok])
            if not math.isfinite(total):
                raise ValueError("R030_R7_HOLD_NONFINITE_MODEL_LOG_PROBABILITY")
            scored.append({
                "uci":u,
                "summed_log_probability":total,
                "mean_log_probability_per_token":total/len(tokens),
                "continuation_tokens":len(tokens),
            })
    return scored


def execute(arm,input_path,support_path,model,tokenizer,torch):
    inp=read_legacy_r5_blind(input_path)
    supports=json.loads(Path(support_path).read_text(encoding="utf-8"))
    examples,legal=validate_arm_and_support(inp,arm,supports)
    rows=[]
    for i,(entry,actions) in enumerate(zip(examples,legal)):
        prompt=prompt_for(entry)
        messages=[{"role":"system","content":"Only output a legal chess move in UCI format. Answer with the UCI code alone."},
                  {"role":"user","content":prompt}]
        ids=tokenizer.apply_chat_template(messages,return_tensors="pt",
                                          add_generation_prompt=True)
        scored=score_all_moves(ids,actions,tokenizer,model,torch)
        rank_sum=choose_ranking(scored)
        rank_mean=choose_ranking(scored,"mean_log_probability_per_token")
        rows.append({
            "ordinal":i,
            "legal_actions_scored":len(actions),
            "prompt_input_tokens":int(ids.shape[-1]),
            "top3_summed_log_probability_uci":[r["uci"] for r in rank_sum[:3]],
            "top3_mean_per_token_uci":[r["uci"] for r in rank_mean[:3]],
            "full_summed_log_probability_ranking":rank_sum,
            "full_mean_per_token_ranking_ucis":[r["uci"] for r in rank_mean],
            "no_target_u_to_score":True,
        })
        print("R030_R7_REAL_TOKEN_SCORER",arm,i,"k",len(actions),
              "top3",rows[-1]["top3_summed_log_probability_uci"],flush=True)
    return {
        "schema":SCHEMA,
        "condition":arm,
        "model_id":MODEL_ID,
        "model_revision":MODEL_REVISION,
        "input_blind_arm_sha256":digest(input_path),
        "legal_support_manifest_sha256":digest(support_path),
        "tokenization":"tokenizer.encode(' '+UCI, add_special_tokens=False) ; NO EOS",
        "prompt_is_exact_R6_instruction_and_chat_template":True,
        "scored_suffix_is_teacher_forced_not_generated":True,
        "primary_metric":"sum log P(UCI continuation tokens | instruction/context)",
        "secondary_metric":"mean log P per UCI token (length-bias sensitivity only)",
        "candidate_lexicographic_tie_break":True,
        "source_target_and_original_reference_never_seen_during_inference":True,
        "explanation_only_uses_board_legal_support_without_FEN_in_model_prompt":True,
        "not_original_Parfenova_200_puzzles":True,
        "not_reference_move_accuracy":True,
        "entries":rows
    }


def main():
    p=argparse.ArgumentParser()
    for field in ("arm","input","legal-support","out"):
        p.add_argument("--"+field,required=True)
    a=p.parse_args()
    if a.arm not in ARMS:
        raise ValueError("R030_R7_HOLD_UNKNOWN_ARM")
    inp=read_legacy_r5_blind(a.input)
    validate_arm_and_support(inp,a.arm,
          json.loads(Path(a.legal_support).read_text(encoding="utf-8")))
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    torch.set_num_threads(2)
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID,revision=MODEL_REVISION,
                                            trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(
        MODEL_ID,revision=MODEL_REVISION,trust_remote_code=False,
        torch_dtype=torch.float32,low_cpu_mem_usage=True)
    model.eval()
    output=execute(a.arm,a.input,a.legal_support,model,tokenizer,torch)
    dest=Path(a.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("R030_R7_REAL_ALL_LEGAL_ARM_COMPLETE",a.arm,digest(dest),flush=True)


if __name__=="__main__":
    main()
