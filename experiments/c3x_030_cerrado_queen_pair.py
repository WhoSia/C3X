import json
import sys
import subprocess

import chess


FEN = "1r3rk1/2pq1ppp/4pn2/1b2B3/2p5/6P1/3PPPBP/2RQ1RK1 w - - 1 16"
CANDIDATES = ("Qc2", "Qa4", "Qb3", "Qe1")

def position(*moves):
    board = chess.Board(FEN)
    for move in ("Bxf6", "gxf6", *moves):
        board.push_san(move)
    return board

def search(engine, board, nodes, move=None):
    def send(command):
        print(command, file=engine.stdin, flush=True)
    send("ucinewgame")
    send("isready")
    for line in engine.stdout:
        if line.strip() == "readyok":
            break
    start = board.root().fen(en_passant="fen")
    moves = " ".join(m.uci() for m in board.move_stack)
    send(f"position fen {start} moves {moves}")
    send(f"go nodes {nodes}" + (f" searchmoves {move.uci()}" if move else ""))
    results = {}
    last_nodes = None
    for line in engine.stdout:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "bestmove":
            result = results[parts[1]]
            return dict(result, last_reported_nodes=last_nodes)
        if parts[0] == "info" and "pv" in parts and "score" in parts:
            idx = parts.index("score")
            last_nodes = int(parts[parts.index("nodes")+1])
            bound = next((b for b in ("lowerbound", "upperbound") if b in parts), None)
            unit, value = parts[idx+1], int(parts[idx+2])
            if not board.turn:
                value = -value
            pv = parts[parts.index("pv")+1:]
            results[pv[0]] = dict(cp=value if unit == "cp" else None, bound=bound,
                          mate=value if unit == "mate" else None,
                          nodes=int(parts[parts.index("nodes")+1]),
                          depth=int(parts[parts.index("depth")+1]),
                          pv=board.variation_san([chess.Move.from_uci(m) for m in pv[:10]]),
                          uci=pv)
    raise RuntimeError("engine exited")


def main():
    mode, path = sys.argv[1:3]
    with subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as engine:
        print("setoption name Threads value 1", file=engine.stdin)
        print("setoption name Hash value 32", file=engine.stdin, flush=True)
        if mode == "root":
            board = position()
            for nodes in (50000, 200000, 1000000, 4000000):
                for san in CANDIDATES:
                    result = search(engine, board, nodes, board.parse_san(san))
                    print(json.dumps(dict(nodes_limit=nodes, candidate=san, **result)), flush=True)
        if mode == "branches":
            first, second = sys.argv[3:5]
            boards = {san: position(san) for san in (first, second)}
            replies = sorted(set.union(*(set(b.legal_moves) for b in boards.values())), key=lambda m: m.uci())
            for move in replies:
                if len(sys.argv) > 6 and move.uci() not in sys.argv[6:]:
                    continue
                for san, board in boards.items():
                    if move not in board.legal_moves:
                        continue
                    label = board.san(move)
                    board.push(move)
                    for constraint in ("free", "d4"):
                        root_move = chess.Move.from_uci("d2d4") if constraint == "d4" else None
                        if root_move is not None and root_move not in board.legal_moves:
                            continue
                        result = search(engine, board, int(sys.argv[5]), root_move)
                        print(json.dumps(dict(candidate=san, reply=label, reply_uci=move.uci(),
                                              constraint=constraint, **result)), flush=True)
                    board.pop()

        if mode == "second":
            board = chess.Board("r1bqr1k1/pp3pp1/2p5/4Q3/2P5/8/PP3PPP/R1B2RK1 w - - 1 16")
            for san in ("Qf4", "Qc3"):
                move = board.parse_san(san)
                for budget in (200000, 1000000):
                    print(json.dumps(dict(candidate=san, nodes_limit=budget,
                                          **search(engine, board, budget, move))), flush=True)
                board.push(move)
                for reply in sorted(board.legal_moves, key=lambda m: m.uci()):
                    label = board.san(reply)
                    board.push(reply)
                    print(json.dumps(dict(candidate=san, reply=label, reply_uci=reply.uci(),
                                          **search(engine, board, 120000))), flush=True)
                    board.pop()
                board.pop()
        if mode == "candidate_plan":
            for reply in ("Rfd8", "Rb6", "Kg7", "c6", "Ba4", "c5", "Rbd8"):
                for san, continuation in (("Qc2", "Qc3"), ("Qe1", "Rc2")):
                    board = position(san, reply)
                    move = board.parse_san(continuation)
                    print(json.dumps(dict(candidate=san, reply=reply, constrained=continuation,
                                          **search(engine, board, 1000000, move))), flush=True)
        print("quit", file=engine.stdin, flush=True)

if __name__ == "__main__":
    main()
