from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import chess
import chess.engine
import chess.pgn

from c3x_explain.core import candidate_packet
from c3x_g10.demand_validity import (
    annotation_control_stats,
    adjudicate_demand_validity,
    board_key,
    freeze_base_evaluation_bank,
    freeze_final_case_bank,
    load_opening_catalog,
    opening_relation,
    phase_from_board,
    stable_hash,
)
from c3x_g10.loop import demand_from_candidate_packet


def dump(path: str | Path, value: Any) -> None:
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def game_identity(game: chess.pgn.Game) -> str:
    h=game.headers
    return "|".join(str(h.get(k,"?")) for k in ("Event","Site","Date","Round","White","Black"))


def _mainline_nodes(game: chess.pgn.Game):
    node=game
    while node.variations:
        child=node.variation(0)
        yield node, child
        node=child


def case_from_position(
    *,
    source_id: str,
    source_month: str,
    game: chess.pgn.Game,
    board: chess.Board,
    moves_before: list[str],
    child: chess.pgn.ChildNode,
    ply: int,
    opening_catalog: list[dict[str,Any]],
    p0: dict[str,Any] | None,
    annotation_label: bool | None = None,
) -> dict[str,Any]:
    move=child.move
    h=game.headers
    opening=opening_relation(moves_before,opening_catalog)
    initial_fen=h.get("FEN") or chess.STARTING_FEN
    cid=stable_hash({
        "source_id":source_id,
        "game_id":game_identity(game),
        "ply":ply,
        "position_key":board_key(board.fen()),
        "played":move.uci(),
    })[:24]
    clock=child.clock()
    return {
        "case_id":cid,
        "source_id":source_id,
        "source_month":source_month,
        "game_id":game_identity(game),
        "event":h.get("Event"),
        "site":h.get("Site"),
        "date":h.get("Date"),
        "round":h.get("Round"),
        "white":h.get("White"),
        "black":h.get("Black"),
        "white_elo":h.get("WhiteElo"),
        "black_elo":h.get("BlackElo"),
        "initial_fen":initial_fen,
        "moves_before_uci":list(moves_before),
        "ply":ply,
        "position_fen":board.fen(),
        "position_key":board_key(board.fen()),
        "played_uci":move.uci(),
        "played_san":board.san(move),
        "phase":phase_from_board(board),
        "opening":opening,
        "clock_after_move_seconds":clock,
        "p0":p0,
        "annotation_label":annotation_label,
        "fresh_local_certificate_induction_opened":False,
        "authority":"EVALUATION_CASE_ONLY",
    }


def scan_broadcast_source(
    *,
    path: str,
    source_id: str,
    source_month: str,
    engine: chess.engine.SimpleEngine,
    opening_catalog: list[dict[str,Any]],
    game_cap: int,
    max_ply: int,
) -> tuple[list[dict[str,Any]],dict[str,Any]]:
    rows=[]
    games=0
    scanned=0
    admitted=0
    with open(path,encoding="utf-8",errors="replace") as f:
        while games < game_cap:
            game=chess.pgn.read_game(f)
            if game is None:
                break
            if game.headers.get("Variant","Standard") not in ("Standard","From Position"):
                continue
            main_moves=list(game.mainline_moves())
            if len(main_moves)<16:
                continue
            games+=1
            board=game.board()
            moves_before=[]
            for ply,(parent,child) in enumerate(_mainline_nodes(game),1):
                if ply>max_ply:
                    break
                if ply>=4 and not board.is_game_over():
                    cands=candidate_packet(engine,board,3,5000)
                    if len(cands)>=3:
                        q=demand_from_candidate_packet(
                            position_fen=board.fen(),
                            played_uci=child.move.uci(),
                            candidates=cands,
                            source_id=source_id,
                            game_id=game_identity(game),
                            ply=ply,
                        )
                        scanned+=1
                        if q["admitted"]:
                            admitted+=1
                            rows.append(case_from_position(
                                source_id=source_id,
                                source_month=source_month,
                                game=game,
                                board=board,
                                moves_before=moves_before,
                                child=child,
                                ply=ply,
                                opening_catalog=opening_catalog,
                                p0=q,
                            ))
                moves_before.append(child.move.uci())
                board.push(child.move)
    summary={
        "source_id":source_id,
        "source_month":source_month,
        "games_scanned":games,
        "positions_scanned":scanned,
        "p0_admitted":admitted,
        "p0_admit_rate":None if scanned==0 else admitted/scanned,
    }
    return rows,summary


def annotation_control_bank(
    *,
    path: str,
    opening_catalog: list[dict[str,Any]],
    positive_target: int,
    negative_target: int,
) -> dict[str,Any]:
    positives=[]
    negatives=[]
    games=0
    with open(path,encoding="utf-8",errors="replace") as f:
        while True:
            game=chess.pgn.read_game(f)
            if game is None:
                break
            if game.headers.get("Variant","Standard") not in ("Standard","From Position"):
                continue
            games+=1
            board=game.board()
            moves_before=[]
            for ply,(parent,child) in enumerate(_mainline_nodes(game),1):
                explicit=bool((child.comment or "").strip() or child.nags or len(child.variations)>1)
                if ply>=4 and not board.is_game_over():
                    row=case_from_position(
                        source_id="LICHESS_TATA_STEEL_2026_ANNOTATIONS",
                        source_month="2026-01",
                        game=game,
                        board=board,
                        moves_before=moves_before,
                        child=child,
                        ply=ply,
                        opening_catalog=opening_catalog,
                        p0=None,
                        annotation_label=explicit,
                    )
                    if explicit:
                        positives.append(row)
                    else:
                        negatives.append(row)
                moves_before.append(child.move.uci())
                board.push(child.move)

    positives.sort(key=lambda x: stable_hash(x["case_id"]))
    selected_pos=positives[:positive_target]
    want_by_phase={}
    for x in selected_pos:
        want_by_phase[x["phase"]]=want_by_phase.get(x["phase"],0)+1

    neg_by_phase={}
    for x in negatives:
        neg_by_phase.setdefault(x["phase"],[]).append(x)
    for xs in neg_by_phase.values():
        xs.sort(key=lambda x: stable_hash(x["case_id"]))
    selected_neg=[]
    for phase,n in sorted(want_by_phase.items()):
        selected_neg.extend(neg_by_phase.get(phase,[])[:n])
    if len(selected_neg)<negative_target:
        used={x["case_id"] for x in selected_neg}
        remainder=sorted((x for x in negatives if x["case_id"] not in used),key=lambda x:stable_hash(x["case_id"]))
        selected_neg.extend(remainder[:negative_target-len(selected_neg)])
    selected_neg=selected_neg[:negative_target]

    payload={
        "schema":"c3x-g10-p1-annotation-control-bank-v1",
        "source_games":games,
        "selection_rule":"stable-hash annotated decisions; matched unannotated by phase then stable-hash fill",
        "annotation_used_for_final_case_selection":False,
        "certificate_outcomes_opened":False,
        "positive_cases":selected_pos,
        "negative_cases":selected_neg,
    }
    payload["bank_sha256"]=stable_hash({"positive":selected_pos,"negative":selected_neg})
    return payload


def cmd_pool(args):
    openings=load_opening_catalog(sorted(Path(args.openings_dir).glob("[abcde].tsv")))
    engine=chess.engine.SimpleEngine.popen_uci(args.stockfish)
    try:
        if "Threads" in engine.options:
            engine.configure({"Threads":1})
        if "Hash" in engine.options:
            engine.configure({"Hash":16})
        all_rows=[]
        summaries=[]
        for spec in args.source:
            source_id,month,path=spec.split("|",2)
            rows,s=scan_broadcast_source(
                path=path,source_id=source_id,source_month=month,engine=engine,
                opening_catalog=openings,game_cap=args.game_cap,max_ply=args.max_ply,
            )
            all_rows.extend(rows);summaries.append(s)
    finally:
        engine.quit()

    base=freeze_base_evaluation_bank(all_rows)
    control=annotation_control_bank(
        path=args.annotation_pgn,
        opening_catalog=openings,
        positive_target=args.annotation_positive_target,
        negative_target=args.annotation_negative_target,
    )
    pool_summary={
        "schema":"c3x-g10-p1-pool-summary-v1",
        "sources":summaries,
        "positions_scanned":sum(x["positions_scanned"] for x in summaries),
        "p0_admitted":sum(x["p0_admitted"] for x in summaries),
        "p0_admit_rate":(
            None if sum(x["positions_scanned"] for x in summaries)==0 else
            sum(x["p0_admitted"] for x in summaries)/sum(x["positions_scanned"] for x in summaries)
        ),
        "admitted_pool_n":len(all_rows),
        "base_evaluation_bank_n":len(base["cases"]),
        "base_evaluation_bank_sha256":base["bank_sha256"],
        "annotation_control_positive_n":len(control["positive_cases"]),
        "annotation_control_negative_n":len(control["negative_cases"]),
        "annotation_control_sha256":control["bank_sha256"],
        "maia_outcomes_opened":False,
        "cross_engine_outcomes_opened":False,
        "certificate_outcomes_opened":False,
    }
    dump(args.out_pool,pool_summary)
    dump(args.out_base,base)
    dump(args.out_control,control)


def cmd_adjudicate(args):
    pool=json.load(open(args.pool,encoding="utf-8"))
    rows=[]
    for p in args.score:
        x=json.load(open(p,encoding="utf-8"))
        rows.extend(x.get("cases") or [])
    base=[x for x in rows if x.get("case_kind")=="base"]
    controls=[x for x in rows if x.get("case_kind")=="annotation_control"]
    bank=freeze_final_case_bank(base)
    instruments=json.load(open(args.instrument_status,encoding="utf-8"))
    court=adjudicate_demand_validity(
        pool_summary=pool,
        scored_base_rows=base,
        scored_controls=controls,
        final_bank=bank,
        instrument_status=instruments,
    )
    court["score_case_count"]=len(rows)
    court["base_score_count"]=len(base)
    court["control_score_count"]=len(controls)
    court["annotation_control_recomputed"]=annotation_control_stats(controls)
    dump(args.out_bank,bank)
    dump(args.out_court,court)
    dump(args.out_scores,{"schema":"c3x-g10-p1-score-table-v1","cases":rows})


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)

    p=sub.add_parser("pool")
    p.add_argument("--source",action="append",required=True,help="source_id|YYYY-MM|pgn_path")
    p.add_argument("--stockfish",required=True)
    p.add_argument("--openings-dir",required=True)
    p.add_argument("--annotation-pgn",required=True)
    p.add_argument("--game-cap",type=int,default=24)
    p.add_argument("--max-ply",type=int,default=70)
    p.add_argument("--annotation-positive-target",type=int,default=24)
    p.add_argument("--annotation-negative-target",type=int,default=24)
    p.add_argument("--out-pool",required=True)
    p.add_argument("--out-base",required=True)
    p.add_argument("--out-control",required=True)
    p.set_defaults(func=cmd_pool)

    p=sub.add_parser("adjudicate")
    p.add_argument("--pool",required=True)
    p.add_argument("--score",action="append",required=True)
    p.add_argument("--instrument-status",required=True)
    p.add_argument("--out-bank",required=True)
    p.add_argument("--out-court",required=True)
    p.add_argument("--out-scores",required=True)
    p.set_defaults(func=cmd_adjudicate)

    args=ap.parse_args();args.func(args)


if __name__=="__main__":
    main()
