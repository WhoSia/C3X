"""R25: generate Korean provenance cards and prospective plan tests from R24 receipts."""

import argparse
import json
from pathlib import Path

from c3x_plan_evidence import audit, required_plan_trial


def synthesize(payload):
    if payload.get("schema") != "C3X_030_R25_FORK_EVIDENCE_V1":
        raise ValueError("Unsupported evidence schema")
    results = []
    for case in payload["cases"]:
        result = audit(case["case_id"], case["reports"], judge=case.get("judge"),
                       replay_verified=False)
        results.append({"audit": result.as_dict(), "next_trial": required_plan_trial(result)})
    return {"schema": "C3X_030_R25_PLAN_AUDIT_V1", "source_archive": payload["raw_archive"],
            "source_sha256": payload["archive_sha256"], "results": results}


def korean_markdown(data):
    lines = ["# Explainable Stockfish · 같은 수의 여러 미래", "",
             "이미 공개된 R24 개발 국면을 다시 분류했어. 이번 실행은 과거 재현 기록을 참조하며 원시 엔진을 새로 재실행하거나 사람 대상 검증을 하지 않았어.", ""]
    for entry in data["results"]:
        result = entry["audit"]
        values = result["native_values"]
        equality = "내부값도 동일" if values[0] == values[1] else f"표시값만 동일 (내부값 {values[0]} / {values[1]})"
        side = "백" if result["chooser"] == "white" else "흑"
        lines.extend([f"## {result['case_id']}", "",
                      f"추천 UCI {result['recommendation']}, 표시 평가 {result['displayed_cp']:+d}cp, {equality}.",
                      f"공통 수순 뒤 {result['first_divergence_ply']}번째 반수에서 {side}의 "
                      f"{result['first_moves'][0]} / {result['first_moves'][1]}가 갈렸어.", "",
                      ("백의 후속 선택이 달라진 사례야." if result["chooser"] == "white" else
                       "백의 계획이 달라졌다는 뜻이 아니라, 엔진이 예측한 흑의 응수가 달라진 사례야."), " ",
                      "| 독립 심판 깊이 | 상대적으로 높은 평가를 받은 수 | 격차 |",
                      "| ---: | --- | ---: |"])
        for row in result["judge_order"]:
            preferred = row["preferred"] if row["preferred"] is not None else "판정 보류"
            margin = str(row["margin_cp"]) + "cp" if row["margin_cp"] is not None else "—"
            lines.append(f"| {row['depth']} | {preferred} | {margin} |")
        messages = {"DEPTH_SENSITIVE_FORK_PREFERENCE": "심판 깊이에 따라 두 갈래의 우열이 뒤집혔어.",
                    "JUDGE_ORDER_STABLE_AT_TESTED_DEPTHS": "시험한 심판 깊이에서는 두 갈래의 우열이 같았어.",
                    "NO_INDEPENDENT_JUDGEMENT": "독립 심판 결과가 없어.",
                    "INCONCLUSIVE_JUDGEMENT": "독립 심판 판정을 보류해."}
        lines.extend(["", messages[result["verdict"]],
                      "**증거의 한계:** PV 두 개는 관측한 후속 경로야. 두 수의 전략적 목표가 동일하거나 다르다는 증명도, NNUE가 특정 특징 때문에 골랐다는 증명도 아니야.",
                      f"**다음 검증:** {entry['next_trial']['question']}", ""])
    lines.extend(["## 상태", "",
                  "- 소스 출력과 독립 판정: 기존 R24 자료를 재사용한 분석",
                  "- 실제 TT·NNUE 개입에 의한 이 분기의 인과성: **미확인**",
                  "- 다른 상대 응수에서 계획이 유지되는지: **미시험**",
                  "- 사람이 새로운 수순을 더 잘 이해하는지: **미시험**", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    output = synthesize(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(output, indent=2, ensure_ascii=False) if args.format == "json" else korean_markdown(output))


if __name__ == "__main__":
    main()
