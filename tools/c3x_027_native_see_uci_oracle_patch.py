from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out-manifest',required=True);a=p.parse_args()
f=Path(a.source)/'src/uci.cpp';s=f.read_text()
old='      else if (token == "isready")    sync_cout << "readyok" << sync_endl;'
assert s.count(old)==1
new='''      else if (token == "c3xsee") {
          std::string notation; int threshold;
          if (is >> notation >> threshold) {
              Move mm = UCI::to_move(pos, notation);
              if (mm == MOVE_NONE)
                  sync_cout << "c3xsee invalid" << sync_endl;
              else {
                  Bitboard occupied = 0;
                  const bool yes = pos.see_ge(mm, occupied, Value(threshold));
                  sync_cout << "c3xsee " << notation << " " << threshold << " " << int(yes)
                            << " " << (unsigned long long)occupied << sync_endl;
              }
          } else sync_cout << "c3xsee bad_arguments" << sync_endl;
      }
'''+old
s=s.replace(old,new,1);f.write_text(s)
Path(a.out_manifest).write_text(json.dumps({'schema':'c3x027-native-SEE-UCI-read-only-oracle','original_source_move_generation_untouched':True,'read_only_command':'c3xsee','supports_occupied_output':True})+'\n')
print('C3X027_SEE_ORACLE_PATCH_PASS')
