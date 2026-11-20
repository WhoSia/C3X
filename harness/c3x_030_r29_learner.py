"""Build matched lesson arms and score a threat plus conditional plan on unseen replies."""
import argparse
from html import escape
import json
from pathlib import Path

import chess

from c3x_030_r27_learner_items import legal_witnesses
from c3x_030_r27_learner_packet import board_html, page
from c3x_030_r29_local_tt_move import write

BOARD_REASON = (
    "…Nd7을 두면 d7 나이트가 c5 비숍을 바로 공격해. …a4를 먼저 두면 백은 "
    "b3 폰을 b4로 밀어 c5를 지킬 수 있어. 나이트가 나중에 비숍을 잡으면 "
    "b4의 폰이 그 나이트를 잡을 수 있는지 확인해."
)


def trace_text(proof):
    sham, mask, restore = (proof["arms"][mode] for mode in ("sham", "mask", "restore"))
    if (not sham["cutoffs"] or mask["cutoffs"] or sham != restore
            or any(arm["best"]["move"] != "f6d7" for arm in (sham, mask))
            or sham["direct_child"]["child_value"] != mask["direct_child"]["child_value"]
            or sham["target_candidate"]["update"] != "0" or mask["target_candidate"]["update"] != "0"):
        raise ValueError("Unexpected source claims for lesson")
    return (
        "Stockfish가 …Nd7을 선두에 올린 탐색에서 …a4를 따로 확인했어. "
        "그때 엔진은 저장해 둔 값으로 탐색을 끝냈어. 그 값만 가리고 다시 돌리자 "
        "백의 bxa4를 실제로 탐색했지만 반환값과 추천은 같았어."
    )


def lesson(fen, condition, proof):
    if condition not in ("A", "B", "C"):
        raise ValueError("Expected one of A, B and C")
    standard = (
        "<p>흑 차례야. 후보인 31…Nd7과 31…a4 중에 한 수를 먼저 골라 봐.</p>"
        + board_html(fen) + "<details><summary>해설 보기</summary><section>"
        "<p>Stockfish 16 추천은 31…Nd7, 흑 관점 −2.57이야.</p>"
        "<p>기본 탐색 31…Nd7 32.Rxd7 Qxd7</p>"
        "<p>별도 실행의 대안 31…a4 32.Rdd1 Nd7</p>"
    )
    if condition in ("B", "C"):
        standard += f"<p>{escape(BOARD_REASON)}</p>"
    if condition == "C":
        standard += f"<aside>{escape(trace_text(proof))}</aside>"
    return page("흑의 두 후보 수", standard + "</section></details>")


def build_key(items):
    out = {}
    for group in ("near", "transfer"):
        for item_id, row in items[group].items():
            state = chess.Board(row["fen"])
            knight = chess.parse_square(row["knight"])
            threatened = sorted(state.attacks(knight) & state.pieces(chess.BISHOP, state.turn))
            if threatened != [chess.parse_square(row["bishop"])]:
                raise ValueError(f"Target knight has an ambiguous bishop threat in {item_id}")
            plans = {}
            for pawn in state.pieces(chess.PAWN, state.turn):
                plans.update(legal_witnesses(state, pawn, threatened[0], knight))
            out[item_id] = {"group": group, "fen": state.fen(), "knight": row["knight"],
                            "threat": row["bishop"], "plans": plans}
    return out


def assessment(keys):
    html = [
        "<p>해설을 닫고 풀어 봐. 표시된 상대 나이트의 공격 범위에 들어오는 우리 비숍의 칸을 적어. "
        "그 비숍을 지키려고 폰을 같은 파일로 밀 수 있는지도 확인해. 폰을 민 뒤 상대 나이트가 "
        "비숍을 잡고 내 폰이 그 나이트를 잡는 수순이 모두 합법이어야 해. "
        "가능하면 첫 폰 수를, 불가능하면 ‘없음’을 적어.</p>"
    ]
    for group, heading in (("near", "같은 기보의 새 응수"), ("transfer", "다른 기보")):
        html.append(f"<h2>{heading}</h2>")
        for item_id, row in keys.items():
            if row["group"] != group:
                continue
            side = "백" if chess.Board(row["fen"]).turn else "흑"
            html.append(f"<section><h3>{item_id} · {side} 차례</h3>" + board_html(row["fen"], (row["knight"],))
                        + f"<label>공격받는 비숍의 칸 <input name='{item_id}-threat'></label>"
                        + f"<label>첫 폰 수 또는 없음 <input name='{item_id}-plan'></label></section>")
    html.append("<p>답은 따로 기록해 줘. 이 페이지의 입력 칸은 답을 전송하지 않아.</p>")
    return page("응수가 바뀐 뒤에도 비숍을 지킬 수 있을까?", "".join(html))


def score(keys, responses):
    if responses.keys() - keys.keys():
        raise ValueError("Unknown assessment item")
    results = {}
    for item_id, row in keys.items():
        answer = responses.get(item_id, {})
        threat = answer.get("threat", "").strip().lower()
        plan = answer.get("plan", "").strip()
        good_threat = threat == row["threat"]
        good_plan = plan in ("없음", "none") and not row["plans"]
        if plan and plan not in ("없음", "none"):
            try:
                move = chess.Board(row["fen"]).parse_san(plan)
                good_plan = move.uci() in row["plans"]
            except ValueError:
                pass
        results[item_id] = {"group": row["group"], "threat": good_threat, "plan": good_plan,
                            "both": good_threat and good_plan, "incomplete": not (threat and plan)}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for file in ("items", "proof", "output"):
        parser.add_argument(file, type=Path)
    modes = parser.add_subparsers(dest="mode", required=True)
    modes.add_parser("packet")
    modes.add_parser("score").add_argument("responses", type=Path)
    args = parser.parse_args()
    items = json.loads(args.items.read_text())
    proof = json.loads(args.proof.read_text())
    if (items["cohort_sha256"] != proof["frozen"]["assets"]["cohort"]
            or items["lesson"]["case"] != proof["frozen"]["case"]):
        raise ValueError("Lesson and source proof identify different games")
    keys = build_key(items)
    if args.mode == "score":
        write(args.output, score(keys, json.loads(args.responses.read_text())))
        return
    public, private = (args.output / "participant", args.output / "organizer")
    public.mkdir(parents=True)
    private.mkdir()
    for condition in ("A", "B", "C"):
        (public / f"lesson-{condition}.html").write_text(
            lesson(items["lesson"]["fen"], condition, proof), encoding="utf-8")
    (public / "assessment.html").write_text(assessment(keys), encoding="utf-8")
    write(private / "key.json", keys)


if __name__ == "__main__":
    main()
