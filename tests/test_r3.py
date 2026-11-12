"""Check the inverse sensitivity units and retention endpoints independently."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from r3_design import audit, required_impact


class R3Tests(unittest.TestCase):
    def test_one_percent_quote_ratio_under_each_retention(self):
        for retention, exposure_in_hundreds in [(0, 3), (.5, 4), (1, 5)]:
            bp = required_impact([200, 300], retention, 1)
            reconstructed = 100 * math.expm1(bp / 10000 * exposure_in_hundreds)
            self.assertAlmostEqual(reconstructed, 1)

    def test_observed_path_does_not_populate_counterfactual(self):
        result = audit()
        self.assertEqual(result['months'], 21)
        self.assertEqual(result['months_with_nonauction_gross_both'], 0)
        self.assertLess(result['observed_quote_change_pct'], 0)
        self.assertIsNone(result['identified_no_purchase_path'])
        self.assertIsNone(result['empirical_gap_interval'])
