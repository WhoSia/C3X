"""Check the R34 source-event match and absence handling."""
import unittest

from c3x_030_r34_depth import event_match
from c3x_030_r33_replay import PRETREATMENT


class R34Tests(unittest.TestCase):
    def test_target_identity_and_absence(self):
        target={key:str(i) for i,key in enumerate(PRETREATMENT)}
        target["event"]="12"
        present={"open":dict(target),"close":{"event":"12","stopped":"0"}}
        self.assertEqual(event_match([present],target),present)
        self.assertIsNone(event_match([],target))
        self.assertIsNone(event_match([present],dict(target,event="13")))

    def test_changed_window_and_duplicate_event_rejected(self):
        target={key:str(i) for i,key in enumerate(PRETREATMENT)}
        target["event"]="12"
        changed={"open":dict(target,beta="999"),"close":{"event":"12"}}
        with self.assertRaisesRegex(ValueError,"different target"):
            event_match([changed],target)
        with self.assertRaisesRegex(ValueError,"different target"):
            event_match([changed,changed],target)


if __name__=="__main__":
    unittest.main()
