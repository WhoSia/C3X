"""Generate offline R27 lesson variants and score legal-move practice."""
import argparse
from html import escape
import json
from pathlib import Path

import chess

from c3x_030_r27_learner_items import legal_witnesses

STYLE = """
:root {color-scheme: light; font-family: system-ui, sans-serif; color: #182720; background: #f6f5ef}
body {margin: 0 auto; padding: 2rem 1.15rem 3rem; max-width: 56rem; line-height: 1.6}
h1, h2 {line-height: 1.25}
section {background: white; border: 1px solid #d7dbd0; border-radius: .6rem; padding: 1rem; margin: 1rem 0}
table {border-collapse: collapse; margin: 1rem auto}
th {padding: .15rem .4rem; color: #34443a; font-weight: 550}
td {width: clamp(1.65rem, 7.5vw, 3rem); height: clamp(1.65rem, 7.5vw, 3rem);
    text-align: center; font: clamp(1.25rem, 4.8vw, 2.1rem) 'DejaVu Sans', sans-serif}
.light {background: #f1ead3} .dark {background: #a8b29a}
.mark {outline: .19rem inset #795000; outline-offset: -.23rem}
aside {background: #f0f3ec; padding: .75rem 1rem; border-radius: .4rem}
summary {cursor: pointer; font-weight: 650}
label {display: block; margin: .55rem 0}
input {font: inherit; max-width: 100%}
@media print { section { break-inside: avoid; } input {border: none; border-bottom: 1px solid} }
"""


def board_html(fen, marked=()):
    position = chess.Board(fen)
    files = "".join(f"<th scope='col'>{file}</th>" for file in chess.FILE_NAMES)
    ranks = []
    for rank in reversed(range(8)):
        cells = []
        for file in range(8):
            square = chess.square(file, rank)
            name = chess.square_name(square)
            value = position.piece_at(square)
            side = ("White" if value.color else "Black") if value else ""
            caption = f"{name} {side} {chess.piece_name(value.piece_type) if value else 'empty'}"
            background = "light" if (rank + file) % 2 else "dark"
            extra = " mark" if name in marked else ""
            piece = value.unicode_symbol() if value else ""
            cells.append(f"<td class='{background}{extra}' aria-label='{caption}'>{piece}</td>")
        ranks.append(f"<tr><th scope='row'>{rank + 1}</th>{''.join(cells)}</tr>")
    return f"<table aria-label='Chess board'><thead><tr><th></th>{files}</tr></thead><tbody>{''.join(ranks)}</tbody></table>"


def page(title, contents):
    return (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{escape(title)}</title><style>{STYLE}</style></head>"
            f"<body><main><h1>{escape(title)}</h1>{contents}</main></body></html>\n")


def setup_text():
    return ("Stockfish 16의 기본 설정과 한 스레드에서 3만 2천 노드를 요청했어. "
            "현재 국면에는 흑의 합법수가 34개 있어. 시작부터 둔 실제 수순을 엔진에 넣고, "
            "각 탐색은 초기 상태에서 새로 시작했어.")


def trace_text(proof):
    original, masked = (proof["arms"][arm] for arm in ("baseline", "both_off"))
    foils = original["candidate_records"]["a5a4"]
    if len(foils) != 1 or foils[0]["window_relation"] != "upper":
        raise ValueError("Unexpected source evidence for the foil")
    if (original["best"]["move"], masked["best"]["move"]) != ("f6d7", "a5a4"):
        raise ValueError("Unexpected recommendation")
    return (f"기본 탐색의 내부 {original['attempt']['iteration']}번째 깊이에서 …Nd7이 선두였고, "
            "뒤이어 본 …a4는 현재 선두를 넘지 못했어. "
            f"두 TT 읽기 경로를 함께 끈 실행은 {masked['attempt']['iteration']}번째 깊이의 …a4를 남겼어. "
            "이 기록은 각 실행에서 선택이 남은 경위를 보여줘.")


def lesson_html(fen, arm, proof):
    if arm not in ("A", "B", "C"):
        raise ValueError("Unknown lesson variant")
    base = (
        "<p>흑 차례야. 후보는 <code>31…Nd7</code>과 <code>31…a4</code>야. 풀이를 열기 전에 먼저 한 수를 골라 봐.</p>"
        + board_html(fen) +
        "<details><summary>풀이 열기</summary><section><h2>엔진 분석</h2>"
        "<p>Stockfish 16의 기본 탐색은 흑 관점 −257 cp로 <strong>31…Nd7</strong>을 추천했어.</p>"
        "<p>기본 실행의 수순 <code>31…Nd7 32.Rxd7 Qxd7</code></p>"
        "<p>별도 실행의 후보 수순 <code>31…a4 32.Rdd1 Nd7</code></p></section>"
    )
    if arm in ("B", "C"):
        panel = trace_text(proof) if arm == "C" else setup_text()
        base += (
            "<section><h2>c5 비숍을 두고 갈리는 지점</h2>"
            "<p>…Nd7은 d7 나이트로 c5 비숍을 바로 공격해. …a4를 먼저 두면 백은 "
            "b3 폰을 b4로 전진시켜 c5를 지킬 차례를 얻어. 이어 …Nd7을 두더라도 "
            "백이 비숍을 폰으로 지키고 있는 국면이야.</p>"
            "<p>다른 응수에서는 비숍의 위치와 폰이 전진할 칸을 다시 확인해.</p>"
            f"<aside>{escape(panel)}</aside></section>"
        )
    return page("같은 국면, 두 후보 수", base + "</details>")


def assessment_html(items):
    parts = ["<p>풀이 예시를 닫고 이 페이지를 풀어 봐. 각 국면에서 지정된 폰을 같은 파일로 "
             "전진시킨 다음, 상대가 지정된 나이트로 비숍을 잡고, 다시 그 폰으로 나이트를 잡는 "
             "세 수가 모두 합법인 경우를 찾아 줘. 가능하면 첫 폰 수를 적어 줘.</p>"]
    for category, heading in (("near", "같은 기보의 다른 응수"), ("transfer", "새 기보")):
        parts.append(f"<h2>{heading}</h2>")
        for key, row in items[category].items():
            pawn, bishop, knight = (row[field] for field in ("pawn", "bishop", "knight"))
            side = "백" if chess.Board(row["fen"]).turn else "흑"
            parts.append(f"<section><h3>{key}</h3><p>{side} 차례 · 내 폰 {escape(pawn)} · "
                         f"내 비숍 {escape(bishop)} · 상대 나이트 {escape(knight)}</p>"
                         + board_html(row["fen"], (pawn, bishop, knight)) +
                         f"<label for='{key}-answer'>가능 / 불가능 / 모르겠음 "
                         f"<input id='{key}-answer' autocomplete='off'></label>"
                         f"<label for='{key}-move'>첫 폰 수 <input id='{key}-move' autocomplete='off'></label>"
                         "</section>")
    parts.append("<p>답을 종이나 별도 응답 파일에 옮겨 줘. 이 문서는 답안을 저장하거나 전송하지 않아.</p>")
    return page("폰이 비숍을 지킬 수 있을까?", "\n".join(parts))


def score(items, responses):
    by_item = {**items["near"], **items["transfer"]}
    if not isinstance(responses, dict) or set(responses) - set(by_item):
        raise ValueError("Unexpected response ID")
    summaries = {}
    for category in ("near", "transfer"):
        scored = {}
        for key, item in items[category].items():
            row = responses.get(key, {"verdict": "missing"})
            verdict = row["verdict"]
            if verdict not in {"yes", "no", "abstain", "missing"}:
                raise ValueError(f"Unknown verdict: {key}")
            board = chess.Board(item["fen"])
            pawn, bishop, knight = (chess.parse_square(item[field]) for field in ("pawn", "bishop", "knight"))
            options = legal_witnesses(board, pawn, bishop, knight)
            if options != item["witnesses"]:
                raise ValueError(f"Key differs from legal replay: {key}")
            first = None
            if verdict == "yes":
                try:
                    first = board.parse_san(row.get("move", "")).uci()
                except ValueError:
                    pass
            correct = (not options and verdict == "no") or (verdict == "yes" and first in options)
            scored[key] = {"verdict": verdict, "correct": correct}
        summaries[category] = {"correct": sum(row["correct"] for row in scored.values()),
                               "total": len(scored), "items": scored}
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("items", type=Path)
    modes = parser.add_subparsers(dest="mode", required=True)
    packet = modes.add_parser("packet")
    packet.add_argument("proof", type=Path)
    packet.add_argument("out", type=Path)
    judge = modes.add_parser("score")
    judge.add_argument("responses", type=Path)
    args = parser.parse_args()
    items = json.loads(args.items.read_bytes())
    if args.mode == "score":
        print(json.dumps(score(items, json.loads(args.responses.read_bytes())), indent=2))
        return
    proof = json.loads(args.proof.read_bytes())
    if items["cohort_sha256"] != proof["build_identity"]["cohort"] or items["lesson"]["case"] != proof["case"]:
        raise ValueError("Study case and native trace disagree")
    args.out.mkdir(parents=True, exist_ok=False)
    for arm in ("A", "B", "C"):
        (args.out / f"lesson-{arm}.html").write_text(lesson_html(items["lesson"]["fen"], arm, proof), encoding="utf-8")
    (args.out / "assessment.html").write_text(assessment_html(items), encoding="utf-8")


if __name__ == "__main__":
    main()
