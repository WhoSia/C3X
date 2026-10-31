"""C3X 0.29-P9 archival-summary checks. NOT a fresh native Stockfish replay."""
from fractions import Fraction
G={
 (4,"O"):("b5c3","c2c8",(11,12)),
 (4,"F"):("c2c8","c2d1",(9,10,12)),
 (10,"O"):("f8f7","f4g3",(6,8,10,11,12)),
 (10,"F"):("a8e8","f8f7",(6,7,8,10,12))
}
baseline={4:{"b5c3","c2c8"},10:{"f8f7","a8e8"}}
assert G[4,"F"][1] not in baseline[4]
assert G[10,"O"][1] not in baseline[10]
assert G[4,"O"][1] in baseline[4]
assert G[10,"F"][1] in baseline[10]
for (g,w),(old,new,depths) in G.items():
 assert old in baseline[g]
 assert all(1<=d<=12 for d in depths)
 if (g,w)==(4,"F"): assert 11 not in depths and (9 in depths and 12 in depths)
 if (g,w)==(10,"O"): assert 7 not in depths and 9 not in depths
def argmax(scores, priority):
 return sorted(priority,key=lambda move:-scores[move])[0]
for (g,w),(old,new,depths) in G.items():
 moves=sorted(baseline[g]|{new})
 strict={m:int(m==new) for m in moves}
 tied={m:0 for m in moves}
 priority=[new]+[m for m in moves if m!=new]
 assert argmax(strict,moves)==argmax(tied,priority)==new
assert Fraction(64-4,64)==Fraction(15,16)
assert Fraction(54,64)==Fraction(27,32)
assert Fraction(38,64)==Fraction(19,32)
print("P9 archive summary and finite nonidentifiability checks PASS (not raw or native replay)")
