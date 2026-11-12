"""Regression checks for the distinction between a published equation and a target."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import r2_model as model


class ModelTests(unittest.TestCase):
    def test_zero_premium_baseline(self):
        self.assertAlmostEqual(model.baseline(.20, .09, 0, .10, 2), .29)

    def test_derivative_of_printed_objective(self):
        for sigma in (1, 2):
            args = (.10, .13, sigma, .05, .0575)
            step = 1e-6
            numeric = (model.annex_utility(.16 + step, *args)
                       - model.annex_utility(.16 - step, *args)) / (2 * step)
            self.assertAlmostEqual(model.annex_derivative(.16, *args), numeric, places=8)

    def test_two_sides_of_threshold(self):
        args = (.1, .1, .0575)
        r, threshold = model.minimum_intercept(*args)
        self.assertAlmostEqual(threshold * 10000, 635.518374388, places=6)
        for point in (r / 2, 2 * r):
            self.assertGreater(model.average_loss_cost_intercept(point, *args), threshold)

    def test_invalid_slope(self):
        with self.assertRaises(ValueError):
            model.minimum_intercept(.1, .1, 0)
