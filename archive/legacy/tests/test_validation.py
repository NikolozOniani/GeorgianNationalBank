import unittest
from src.validation import reconcile,unmatched_share,zip_integrity,chain_monthly_indices
import tempfile,zipfile,pathlib
class ValidationTests(unittest.TestCase):
 def test_missing_is_not_zero(self):
  self.assertIsNone(reconcile(100,20,None,0,0,0,0)['residual'])
 def test_valuation_not_intervention(self):
  self.assertEqual(reconcile(100,20,0,50,30,0,0)['residual'],0)
 def test_weighted_unmatched(self):
  self.assertEqual(unmatched_share([{'code':'a','expenditure':10,'weight':3},{'code':'b','expenditure':10,'weight':1}],{'a':'01'}),.25)
 def test_zero_denominator(self):
  self.assertIsNone(unmatched_share([],{}))
 def test_crc_failure_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'bad.zip'
   with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_STORED) as z:z.writestr('record.txt',b'known payload')
   raw=p.read_bytes().replace(b'known payload',b'BROKENpayload');p.write_bytes(raw)
   self.assertEqual(zip_integrity(p),'crc_failure')
 def test_malformed_zip_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'bad.zip';p.write_bytes(b'PK\x03\x04truncated')
   self.assertEqual(zip_integrity(p),'structural_failure')
 def test_monthly_chain_and_gap(self):
  self.assertAlmostEqual(chain_monthly_indices([110,90]),-.01)
  with self.assertRaises(ValueError):chain_monthly_indices([110,None,90])
if __name__=='__main__':unittest.main()
