#!/usr/bin/env python3
"""Freeze September 2026 Lichess broadcast 16 distinct games before any engine trial."""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_020_C_March2026_enginefree_blind16 import select_compressed_archive

URL="https://database.lichess.org/broadcast/lichess_db_broadcast_2026-09.pgn.zst"
MAY_SHA="0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61"
JULY_SHA="45d758947b6f224901f2674eaed4dc1dc34f4d5a439ccd62fa408393dd7c2a80"
P11_SHA={
"77a266c9687cf7aef825a74106c8534ffb0a28aa305af25658f5537be795d4eb",
"eb04018fbc16913e5d127558423363fe91fed5ecbd5693ed8b63f1535c7f6943",
"c8cb4b75f3d27b286ee5b4f34e60182c1de4d3ed0731247ff0b47d857c28d984",
"6d67f1931da94169b94337c6b0c945d75cdad0041f3d5a1b25e91519ec2e185b",
"fc4d54041b191daba6ef258bff600b2be3c3994aff7bd60b1922f95cb6c5c15d",
"480a4abc7e9331a0acb6186a242f8343375e2c3266ed89a408f91b6d96da52b7",
"d295dbaf4b42dbca553ba5550ceeaf687649a98a13946465d5ddd71cf0e96373",
"3f19a0c8c5b14635911bfb6b0feaa9b6bb987ad954c6a918149a3176d0001337",
"6245ce09c9c82f90c0e0b6e2fefe2255bae52ca08e77b5f00813114eefddf397"}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 for a in ('zst','may','july','out'):p.add_argument('--'+a,required=True)
 a=p.parse_args()
 if sha(a.may)!=MAY_SHA:raise ValueError("MAY_PRIOR_SOURCE_DRIFT")
 if sha(a.july)!=JULY_SHA:raise ValueError("JULY_PRIOR_SOURCE_DRIFT")
 may=json.loads(Path(a.may).read_text())['per_ecology']['may2026_broadcast']['selected']
 july=json.loads(Path(a.july).read_text())['selected']
 prior=may+july
 fens={r['fen4'] for r in prior};game_hashes={r['source_game_sha256'] for r in prior}|P11_SHA
 chosen,archive_hash,scanned,rejections=select_compressed_archive(a.zst,fens)
 assert len(chosen)==16
 rows=[]
 for k,r in enumerate(chosen):
  assert r['source_game_sha256'] not in game_hashes,"HISTORICAL_GAME_SHA_REUSED"
  board=chess.Board()
  for u in r['full_original_mainline_uci'][:r['source_ply_before_original_move']]:
   mv=chess.Move.from_uci(u)
   assert mv in board.legal_moves
   board.push(mv)
  fen4=" ".join(board.fen(en_passant='fen').split()[:4])
  assert fen4==r['fen4'] and board.is_valid()
  rows.append({'id':k+1,'source_game_sha256':r['source_game_sha256'],
    'source_ordinal':r['source_ordinal'],'fen4':fen4,
    'source_halfmove_clock':board.halfmove_clock,
    'source_fullmove_number':board.fullmove_number,
    'source_ply_before_original_move':r['source_ply_before_original_move'],
    'played_legal_move_uci':r['played_legal_move_uci'],
    'source_root_legal_count':r['source_root_legal_count']})
 assert len(set(x['fen4'] for x in rows))==16
 assert len(set(x['source_game_sha256'] for x in rows))==16
 out={'schema':'c3x027-sept2026-enginefree-source-only16-v1',
      'phase':'SOURCE_ONLY_PRE_NATIVE_TREATMENT',
      'source_url':URL,'license':'CC BY-SA 4.0',
      'attribution':'Lichess broadcasts',
      'license_url':'https://creativecommons.org/licenses/by-sa/4.0/',
      'change_notice':'Extract selected FEN and game SHA; original PGN and player names not redistributed',
      'source_compressed_sha256':archive_hash,
      'prior_may_source_sha256':MAY_SHA,'prior_july_source_sha256':JULY_SHA,
      'prior_game_SHA_count':len(game_hashes),
      'prior_FEN4_count':len(fens),'source_scan_count':scanned,
      'rejected':rejections,'selection_rule':'Existing March C2 selector: first 512 eligible, hash-sort take 16, ply30+SHA8 modulo15; no engine',
      'native_stockfish_treatment_runs':0,'source_games':rows}
 Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print('C3X027_SEPT_SOURCE_FREEZE_PASS',len(rows),sha(a.out),archive_hash,scanned)
if __name__=='__main__':main()
