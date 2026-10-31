import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from c3x_029_p13_nearby_negative_minimax_evaluator import evaluate

def row(i,g,y,game=None):
    return {"case_id":str(i),"game_id":str(game or i),"group":g,"predicted":y}

class P13Tests(unittest.TestCase):
    def test_worst_group_not_average(self):
        data=[row(i,"positive",True) for i in range(1,5)]+[row(i,"negative",False) for i in range(5,9)]+[row(i,"nearby_negative",i!=9) for i in range(9,13)]
        d=evaluate(data)
        self.assertEqual(d["accuracy_by_group"]["nearby_negative"]["correct"],1)
        self.assertEqual(d["worst_group_accuracy"],0.25)
    def test_no_missing_nearby_negative(self):
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):evaluate([row(1,"positive",True),row(2,"negative",False)])
    def test_no_duplicate_case_ids(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATED"):evaluate([row(1,"positive",True),row(1,"negative",False),row(3,"nearby_negative",False)])
    def test_unknown_or_malformed_prediction(self):
        with self.assertRaisesRegex(ValueError,"NOT_BINARY"):evaluate([row(1,"positive",1),row(2,"negative",False),row(3,"nearby_negative",False)])
    def test_no_game_identity(self):
        r=[row(1,"positive",True),row(2,"negative",False),row(3,"nearby_negative",False)]
        r[2]["game_id"]=None
        with self.assertRaisesRegex(ValueError,"GAME_CLUSTER"):evaluate(r)
if __name__=="__main__":unittest.main()
