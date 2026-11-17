"""Render a scoped Stockfish reply experiment as a Korean explanation card."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))

from c3x_030_r25_reply_provenance import CASES, FORK, HINTS
from c3x_030_r25_reply_resource import inspect
from c3x_030_s4l_r10_reply_transport import board_at, digest


def render(case, freeze, result):
    reports = freeze["reports"]
    root = board_at(case["history"])
    after_root = root.copy()
    after_root.push_uci(reports[0]["pv"][0])
    if result["case"] != case["id"] or result["after_root_fen"] != after_root.fen():
        raise ValueError("Experiment refers to a different position")
    board_facts = inspect(case["history"], reports)
    rows = result["rows"]
    for report in reports:
        final = rows[f"{report['depth']}-sham"]["final"]
        if any(report[key] != final[key] for key in ("pv", "move", "cp", "native")):
            raise ValueError("Sham result disagrees with the frozen report")
    rec = root.san(root.parse_uci(reports[0]["move"]))
    lines = [f"# Explainable Stockfish — {rec} 뒤에 갈린 흑의 응수",
             "", f"시작 FEN `{root.fen()}`", "",
             "흑의 첫 응수 한 층에서 지정한 수를 먼저 탐색하게 하고, 최종 PV에 복사된 응수를 기록했어.",
             "", "| 깊이 | 먼저 볼 수를 지정 | 최종 첫 응수 | GUI | 내부값 | 탐색 노드 |",
             "| ---: | --- | --- | ---: | ---: | ---: |"]
    for name, row in rows.items():
        depth, mode = name.split("-")
        final, trace = row["final"], row["reply_trace"]
        if trace["copy"]["reply"] != final["pv"][1] or final["move"] != reports[0]["move"]:
            raise ValueError("Reported move is unconnected to the recorded child reply")
        picker = "엔진 기본 순서" if mode == "sham" else board_facts[HINTS[mode]]["san"]
        label = board_facts[final["pv"][1]]["san"]
        lines.append(f"| {depth} | {picker} | {label} | {final['cp']:+d}cp | "
                     f"{final['native']} | {final['nodes']:,} |")
    lines.extend(["", "개입에 따라 달라진 공개 수순 앞부분", ""])
    for depth, mode in ((12, "be7"), (18, "bh2")):
        for setting in ("sham", mode):
            final = rows[f"{depth}-{setting}"]["final"]
            pv = [root.parse_uci(final["move"])]
            board = root.copy()
            board.push(pv[0])
            for uci in final["pv"][1:7]:
                move = board.parse_uci(uci)
                board.push(move)
                pv.append(move)
            description = "엔진 기본 순서" if setting == "sham" else f"{board_facts[HINTS[setting]]['san']} 먼저"
            lines.append(f"- 깊이 {depth} · {description} · `{root.variation_san(pv)}`")
    checking = board_facts["d6h2"]
    quiet = board_facts["d6e7"]
    evasion, = checking["evasions"]
    if not (checking["check"] and not checking["b4_now"] and quiet["b4_now"]):
        raise ValueError("Board does not support the expected b4 timing contrast")
    lines.extend(["", "## 보드에서 확인한 b4의 타이밍", "",
                  f"…{quiet['san']} 뒤에는 백이 바로 b4를 둘 수 있어. …{checking['san']} 뒤에는 "
                  f"{evasion['san']}이 유일한 합법수야. 이어서 흑의 합법수 "
                  f"{evasion['black_choices']}개 중 {evasion['b4_available']}개에서 백은 다음 차례에 b4를 둘 수 있어.",
                  "", "b4의 합법성은 이 국면과 다음 백 차례를 대상으로 확인했어. b4의 전략적 가치와 "
                  "그 가치가 Qxe2의 선택에 기여한 정도는 후속 실험의 대상이야.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cases", "freeze", "result"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    if (digest(args.cases), digest(args.freeze)) != (CASES, FORK):
        raise ValueError("Unexpected R24 evidence")
    cases, freeze, result = (json.loads(path.read_text()) for path in (args.cases, args.freeze, args.result))
    case = next(row for row in cases["cases"] if row["id"] == freeze["case"])
    print(render(case, freeze, result), end="")


if __name__ == "__main__":
    main()
