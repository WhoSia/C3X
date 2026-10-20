#!/usr/bin/env python3
"""Read-only Stockfish16 see_ge source-branch trace; no search/SEE decision changes."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out-manifest',required=True);a=p.parse_args()
sf=Path(a.source)/'src/position.cpp'
s=sf.read_text()
def once(old,new):
 global s
 if s.count(old)!=1:raise RuntimeError("SEE_BRANCH_ANCHOR_"+str(s.count(old))+" "+old[:70])
 s=s.replace(old,new,1)
once('namespace Stockfish {','namespace Stockfish {\nunsigned long long c3x027_see_trace_mask = 0;')
once('bool Position::see_ge(Move m, Bitboard& occupied, Value threshold) const {','bool Position::see_ge(Move m, Bitboard& occupied, Value threshold) const {\n  c3x027_see_trace_mask = 0;')
once('if (type_of(m) != NORMAL)\n      return VALUE_ZERO >= threshold;',
     'if (type_of(m) != NORMAL) { c3x027_see_trace_mask |= 1ULL<<0; return VALUE_ZERO >= threshold; }')
once('if (swap < 0)\n      return false;',
     'if (swap < 0) { c3x027_see_trace_mask |= 1ULL<<1; return false; }')
once('if (swap <= 0)\n      return true;',
     'if (swap <= 0) { c3x027_see_trace_mask |= 1ULL<<2; return true; }')
once('  while (true)\n  {\n      stm = ~stm;', '  while (true)\n  {\n      c3x027_see_trace_mask |= 1ULL<<3;\n      stm = ~stm;')
once('if (!(stmAttackers = attackers & pieces(stm)))\n          break;',
     'if (!(stmAttackers = attackers & pieces(stm))) { c3x027_see_trace_mask |= 1ULL<<4; break; }')
once('if (pinners(~stm) & occupied)\n      {\n          stmAttackers &= ~blockers_for_king(stm);',
     'if (pinners(~stm) & occupied)\n      {\n          c3x027_see_trace_mask |= 1ULL<<5;\n          const Bitboard c3x027_prior_attackers = stmAttackers;\n          stmAttackers &= ~blockers_for_king(stm);\n          if (stmAttackers != c3x027_prior_attackers) c3x027_see_trace_mask |= 1ULL<<6;')
once('if (!stmAttackers)\n              break;', 'if (!stmAttackers) { c3x027_see_trace_mask |= 1ULL<<17; break; }')
for piece,bit in [('PAWN',7),('KNIGHT',8),('BISHOP',9),('ROOK',10),('QUEEN',11)]:
 # only occurs once in this routine; source also references other functions -> scope search near SEE
 old='if ((bb = stmAttackers & pieces('+piece+')))\n      {'
 once(old,old+'\n          c3x027_see_trace_mask |= 1ULL<<'+str(bit)+';')
once('if ((swap = PawnValueMg - swap) < res)\n              break;',
     'if ((swap = PawnValueMg - swap) < res) { c3x027_see_trace_mask |= 1ULL<<16; break; }')
for piece in ['Knight','Bishop','Rook','Queen']:
 once('if ((swap = '+piece+'ValueMg - swap) < res)\n              break;',
      'if ((swap = '+piece+'ValueMg - swap) < res) { c3x027_see_trace_mask |= 1ULL<<16; break; }')
# The three bishop x-ray refresh sites: pawn, bishop, queen
needle='          attackers |= attacks_bb<BISHOP>(to, occupied) & pieces(BISHOP, QUEEN);'
assert s.count(needle)==2
s=s.replace(needle,needle+'\n          c3x027_see_trace_mask |= 1ULL<<13;',2)
once('          attackers |= attacks_bb<ROOK>(to, occupied) & pieces(ROOK, QUEEN);',
     '          attackers |= attacks_bb<ROOK>(to, occupied) & pieces(ROOK, QUEEN);\n          c3x027_see_trace_mask |= 1ULL<<14;')
once('                      | (attacks_bb<ROOK  >(to, occupied) & pieces(ROOK  , QUEEN));',
     '                      | (attacks_bb<ROOK  >(to, occupied) & pieces(ROOK  , QUEEN));\n          c3x027_see_trace_mask |= 1ULL<<15;')
once('else // KING\n           // If we "capture" with the king but opponent still has attackers,\n           // reverse the result.\n          return (attackers & ~pieces(stm)) ? res ^ 1 : res;',
     'else // KING\n      {\n          c3x027_see_trace_mask |= 1ULL<<12;\n          return (attackers & ~pieces(stm)) ? res ^ 1 : res;\n      }')
sf.write_text(s)
uf=Path(a.source)/'src/uci.cpp';u=uf.read_text()
assert u.count('namespace Stockfish {')==1
u=u.replace('namespace Stockfish {','namespace Stockfish {\nextern unsigned long long c3x027_see_trace_mask;',1)
old='<< " " << (unsigned long long)occupied << sync_endl;'
assert u.count(old)==1
u=u.replace(old,'<< " " << (unsigned long long)occupied\n                            << " " << c3x027_see_trace_mask << sync_endl;',1)
uf.write_text(u)
names=['special','capture_gate_false','origin_gate_true','exchange_loop','no_opponent_attackers','pin_gate','pinned_attacker_filtered','pawn_attacker','knight_attacker','bishop_attacker','rook_attacker','queen_attacker','king_attacker','bishop_xray_refresh','rook_xray_refresh','queen_xray_refresh','swap_early_break','pin_filtered_all']
Path(a.out_manifest).write_text(json.dumps({'schema':'C3X027_NATIVE_SEE_READ_ONLY_BRANCH_MASK','names':names,'original_see_ge_branch_decisions_unchanged':True},indent=2)+'\n')
print('C3X027_BRANCH_TRACE_PATCH_PASS',len(names))
