#!/usr/bin/env python3
"""C3X 0.30/P3 — loopback-only interactive chess analysis HTTP adapter.

Reuses P1 real Stockfish forced-root search and P2 rule-based CCC concepts.
No remote endpoints, API keys, subprocess command construction or network
dependencies. The binding address is intentionally FIXED to loopback.

The historical C3X research causal proof is still HOLD; this is a local
interactive product prototype, not the original CCC learned model.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit

import chess
import chess.engine

from c3x_explain_two_moves import generate, make_markdown, verify_board_and_pair
from c3x_concept_contrast import contrast, markdown_append
from c3x_recursive_strategy import produce as produce_two_layer_strategy
from c3x_metamorphic_gap_audit import case_analysis as analyze_mirror_gap
from c3x_evidence_strategy_commentary import annotate as source_plan_commentary, markdown as strategy_markdown

SCHEMA = "c3x030-p3-local-interactive-product-v1"
MAX_POST_BYTES = 4096
DEFAULT_FEN = chess.STARTING_FEN
FRONTEND = Path(__file__).with_name("c3x_board.html")
ORIGIN_POLICY = "same-origin-localhost-only"


def legal_payload(fen):
    """Fresh legal move list with SAN from the exact current board."""
    if not isinstance(fen, str) or len(fen) > 160:
        raise ValueError("P3_BAD_FEN_LENGTH")
    try:
        board = chess.Board(fen)
    except (ValueError, TypeError) as exc:
        raise ValueError("P3_INVALID_FEN") from exc
    if not board.is_valid() or board.is_game_over(claim_draw=False):
        raise ValueError("P3_INVALID_OR_TERMINAL_BOARD")
    entries = sorted(
        ({"uci": move.uci(), "san": board.san(move)}
         for move in board.legal_moves),
        key=lambda item: item["uci"]
    )
    if not entries:
        raise ValueError("P3_EMPTY_LEGAL_MOVE_SET")
    return {"schema": SCHEMA, "fen": board.fen(en_passant="fen"),
            "turn": "white" if board.turn else "black", "legal_moves": entries}


def request_payload(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_POST_BYTES:
        raise ValueError("P3_REQUEST_TOO_LARGE")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError("P3_MALFORMED_JSON") from exc
    if not isinstance(data, dict) or set(data) != {"fen", "move_a", "move_b"}:
        raise ValueError("P3_UNEXPECTED_REQUEST_FIELDS")
    if not all(isinstance(data[k], str) for k in data):
        raise ValueError("P3_NONSTRING_INPUT")
    if len(data["fen"]) > 160 or any(len(data[k]) > 5 for k in ("move_a", "move_b")):
        raise ValueError("P3_INPUT_LENGTH_LIMIT")
    return data


def analyze_payload(payload, engine):
    original, a, b = verify_board_and_pair(payload["fen"],
                                            payload["move_a"], payload["move_b"])
    original_report = generate(original, a.uci(), b.uci(), engine)
    concept_report = contrast(original, a.uci(), b.uci())
    if (original_report["input_fen"] != concept_report["source_original_fen"]
        or [r["move_uci"] for r in original_report["root_candidates"]]
           != concept_report["root_moves_uci"]):
        raise RuntimeError("P3_HOLD_P1_P2_RESULT_IDENTITY_MISMATCH")
    return {
        "schema": SCHEMA,
        "fen": original_report["input_fen"],
        "engine_report": original_report,
        "concept_report": concept_report,
        "learner_markdown": make_markdown(original_report) +
                            "\n\n" + markdown_append(concept_report),
        "evidence": {
            "native_stockfish": True,
            "rule_exact_chess_features": True,
            "independent_referee": False,
            "all_opponent_replies_judged": False,
            "source_engine_internal_causality_proven": False,
            "chesscom_user_benchmark_performed": False,
        },
    }


def create_handler(engine_path):
    engine_path = str(Path(engine_path).expanduser().resolve())
    if not Path(engine_path).is_file():
        raise ValueError("P3_STOCKFISH_BINARY_MISSING")
    # A lock protects against two simultaneous requests controlling one UCI engine.
    engine_mutex = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def _response(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; script-src 'self'; "
                             "style-src 'self' 'unsafe-inline'; "
                             "connect-src 'self'; img-src 'self' data:; "
                             "base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status, obj):
            self._response(status,
                           json.dumps(obj, ensure_ascii=False,
                                      allow_nan=False).encode("utf-8"),
                           "application/json; charset=utf-8")

        def _is_same_origin(self):
            origin = self.headers.get("Origin")
            if origin is None:
                return True
            host = self.headers.get("Host", "")
            return host in ("127.0.0.1:" + str(self.server.server_port),
                            "localhost:" + str(self.server.server_port)) and origin == "http://" + host

        def do_GET(self):
            path = urlsplit(self.path)
            if path.path == "/" and not path.query:
                self._response(200, FRONTEND.read_bytes(), "text/html; charset=utf-8")
            elif path.path == "/api/health" and not path.query:
                self._json(200, {"schema": SCHEMA, "ready": True,
                                 "network_binding": "127.0.0.1"})
            elif path.path == "/api/legal" and not path.query:
                try:
                    self._json(200, legal_payload(DEFAULT_FEN))
                except ValueError as exc:
                    self._json(422, {"error": str(exc)})
            elif path.path == "/c3x_board.js" and not path.query:
                self._response(200, FRONTEND.with_suffix(".js").read_bytes(),
                               "text/javascript; charset=utf-8")
            else:
                self._json(404, {"error": "P3_UNKNOWN_ROUTE"})

        def do_POST(self):
            path = urlsplit(self.path)
            if path.path not in ("/api/legal", "/api/analyze", "/api/strategy", "/api/mirror") or path.query:
                self._json(404, {"error": "P3_UNKNOWN_ROUTE"})
                return
            if not self._is_same_origin():
                self._json(403, {"error": "P3_FOREIGN_ORIGIN"})
                return
            if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                self._json(415, {"error": "P3_JSON_ONLY"})
                return
            try:
                declared_len = int(self.headers.get("Content-Length", "-1"))
            except ValueError:
                declared_len = -1
            if not 0 <= declared_len <= MAX_POST_BYTES:
                self.close_connection = True
                self._json(413, {"error": "P3_REQUEST_SIZE_LIMIT"})
                return
            raw = self.rfile.read(declared_len)
            try:
                if path.path == "/api/legal":
                    request = json.loads(raw.decode("utf-8"))
                    if not isinstance(request, dict) or set(request) != {"fen"}:
                        raise ValueError("P3_BAD_LEGAL_REQUEST")
                    report = legal_payload(request["fen"])
                    self._json(200, report)
                else:
                    request = request_payload(raw)
                    # Reject malformed / illegal requests before opening ANY
                    # native chess-engine process.
                    verify_board_and_pair(request["fen"],
                                          request["move_a"], request["move_b"])
                    # Synchronous request is deliberately serialized by mutex.
                    # Do not return plausible synthetic results when UCI fails.
                    with engine_mutex:
                        with chess.engine.SimpleEngine.popen_uci(engine_path,
                                                                timeout=120) as engine:
                            if ("stockfish" not in engine.id.get("name", "").lower()
                                or not {"Use NNUE", "Threads", "Hash"}.issubset(engine.options)):
                                raise RuntimeError("P3_HOLD_WRONG_ENGINE")
                            engine.configure({"Use NNUE": False, "Threads": 1, "Hash": 16})
                            if path.path == "/api/strategy":
                                report = produce_two_layer_strategy(
                                    request["fen"], request["move_a"],
                                    request["move_b"], engine, k=2, depth=8)
                                report["evidence_verified_strategy_explanation"] = source_plan_commentary(report)
                                report["evidence_verified_strategy_markdown"] = strategy_markdown(report["evidence_verified_strategy_explanation"])
                            elif path.path == "/api/mirror":
                                report = analyze_mirror_gap(
                                    request["fen"], request["move_a"],
                                    request["move_b"], engine,
                                    case_id="user_selected_fen_local_not_frozen")
                            else:
                                report = analyze_payload(request, engine)
                    self._json(200, report)
            except (ValueError, UnicodeError, KeyError) as exc:
                self._json(422, {"error": str(exc)})
            except (chess.engine.EngineError, chess.engine.EngineTerminatedError,
                    TimeoutError, OSError, RuntimeError) as exc:
                self.log_error("P3 server actual engine failed: %s", str(exc))
                self._json(503, {"error": "P3_ACTUAL_ENGINE_UNAVAILABLE"})

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stockfish", required=True,
                        help="Local original Stockfish binary path")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        raise ValueError("P3_INVALID_LOCAL_PORT")
    with ThreadingHTTPServer(("127.0.0.1", args.port),
                             create_handler(args.stockfish)) as server:
        print("C3X_P3_LOCAL_WEB_READY http://127.0.0.1:" + str(args.port),
              flush=True)
        server.serve_forever(poll_interval=0.2)


if __name__ == "__main__":
    main()
