import unittest
from src.validation import reconcile,unmatched_share
class ValidationTests(unittest.TestCase):
 def test_missing_is_not_zero(self):
  self.assertIsNone(reconcile(100,20,None,0,0,0,0)['residual'])
 def test_valuation_not_intervention(self):
  self.assertEqual(reconcile(100,20,0,50,30,0,0)['residual'],0)
 def test_weighted_unmatched(self):
  self.assertEqual(unmatched_share([{'code':'a','expenditure':10,'weight':3},{'code':'b','expenditure':10,'weight':1}],{'a':'01'}),.25)
 def test_zero_denominator(self):
  self.assertIsNone(unmatched_share([],{}))
if __name__=='__main__':unittest.main()
