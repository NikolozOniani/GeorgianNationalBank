"""Check policy timing, price transmission, conditional expectations and source benchmarks."""
import csv
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import r3_policy_feedback as model


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def two_stage(series, t, window):
    """Explicit repricing pairs, independent of the production convolution/matrix."""
    return sum(series[t-a-b] for a in range(1, window+1) for b in range(window)
               if t >= a+b) / window**2


class PolicyFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.months, cls.gdp, cls.history, cls.weights, _ = model.fx.load_inputs()
        cls.dates = model.episode_calendar(cls.months)
        cls.prices = model.headline()
        cls.intervals = model.meeting_intervals(cls.dates, model.N + len(cls.months))
        cls.rows = read(model.OUT / "monthly.csv")
        cls.impulses = read(model.OUT / "impulses.csv")
        cls.calibrations = read(model.OUT / "calibration.csv")
        cls.central = model.SETTINGS[1]
        cls.b = model.demand_coefficient(cls.intervals[:model.N])
        cls.k = model.calibrate(cls.intervals[:model.N], cls.central, cls.b)

    def scenario(self, months, setting, n=model.N):
        iv = model.meeting_intervals(self.dates, n + len(months))
        b = model.demand_coefficient(iv[:n])
        k = model.calibrate(iv[:n], setting, b)
        return model.episode(months, self.gdp, self.history, self.weights, self.prices, self.dates,
                             iv, setting, k, b, n=n)

    def test_geostat_all_months_and_frozen_fixed_paths(self):
        # Geostat September 2026 bulletin, p. 6, upper chart, printed to one decimal.
        published = [2, 2.4, 3.5, 3.4, 3.5, 4, 4.3, 4.6, 4.8, 5.2, 4.8, 4,
                     4.8, 4.6, 4.3, 5.9, 5.7, 5.8, 5.5, 5.6, 5.6]
        self.assertEqual([round(self.prices[m.month], 1) for m in self.months], published)
        self.assertEqual(len(self.rows), 126)
        reference = read(ROOT / "reports/r3_fixed_rate/monthly.csv")
        for s in model.SETTINGS:
            sub = [r for r in self.rows if r["case"] == s.case.name and r["policy"] == "fixed"]
            for r, other in zip(sub, reference, strict=True):
                self.assertEqual(r["month"], other["month"])
                self.assertEqual(r["no_purchases_gel_per_usd"], other[s.case.name + "_gel_per_usd"])
                self.assertEqual(r["no_purchases_policy_rate_pct"], other["common_policy_rate_pct"])
                self.assertEqual(r["conditional_liquid_fx_usdm"], other["conditional_liquid_fx_usdm"])
                self.assertEqual(r["retained_sales_usdm"], other["retained_sales_usdm"])

    def test_realized_prices_and_meeting_rule_independently(self):
        for s, meta in zip(model.SETTINGS, self.calibrations, strict=True):
            for mode in ("fixed", "endogenous"):
                rows = [r for r in self.rows if r["case"] == s.case.name and r["policy"] == mode]
                x = [100*math.log(float(r["no_purchases_gel_per_usd"])/float(r["observed_gel_per_usd"])) for r in rows]
                i = [float(r["policy_rate_gap_pp"]) for r in rows]
                last = -1
                for t, r in enumerate(rows):
                    fx = float(meta["cpi_fx_loading"]) * (two_stage(x, t, 21)-two_stage(x, t-12, 21))
                    domestic = -float(meta["domestic_rate_loading"]) * two_stage(i, t, 18)
                    self.assertAlmostEqual(fx + domestic, float(r["inflation_gap_pp"]), places=7)
                    self.assertAlmostEqual(domestic, float(r["domestic_rate_inflation_gap_pp"]), places=8)
                    self.assertAlmostEqual(float(r["observed_yoy_inflation_pct"]) + fx + domestic,
                                           float(r["no_purchases_yoy_inflation_pct"]), places=7)
                    prior = i[t-1] if t else 0.
                    if r["mpc_decision_date"]:
                        retain = .75 ** ((t-last)/3)
                        forecast = float(r["meeting_forecast_inflation_gap_12m_ahead_pp"])
                        expected = retain*prior + (1-retain)*s.phi*forecast if mode == "endogenous" else 0.
                        last = t
                    else:
                        self.assertEqual(r["meeting_forecast_inflation_gap_12m_ahead_pp"], "")
                        expected = prior
                    self.assertAlmostEqual(i[t], expected, places=8)

    def test_reference_fx_impulse_and_forward_rate_units(self):
        for s in model.SETTINGS:
            rows = [r for r in self.impulses if r["case"] == s.case.name]
            x = np.array([float(r["unit_fx_gap_log_points"]) for r in rows])
            rate = np.array([float(r["unit_fx_rate_gap_pp"]) for r in rows])
            self.assertAlmostEqual(100*math.expm1(-x[0]/100), 10, places=8)
            self.assertAlmostEqual(float(rows[24]["unit_fx_inflation_gap_pp"]), -s.target, places=8)
            self.assertEqual(float(rows[0]["unit_fx_inflation_gap_pp"]), 0)
            amplitude = x[0] + sum(rate[:12])/12
            policy_irf = [float(r["tightening_rate_gap_pp"]) for r in rows]
            self.assertEqual(policy_irf[0], 1.)
            for t in range(48):
                d = amplitude * 2**(-t/s.case.half_life)
                self.assertAlmostEqual(x[t], d - sum(rate[t:t+12])/12, places=8)
                self.assertAlmostEqual(float(rows[t]["tightening_fx_gap_log_points"]),
                                       -sum(policy_irf[t:t+12])/12, places=8)
        for horizon in (0, 6, 12, 24):
            s = replace(self.central, parity=horizon, phi=0)
            # A 100 bp innovation persists if future meetings are disabled.
            p = model.project(np.zeros(100), np.zeros(100), s, self.k, self.b, rate_shock=1)
            self.assertAlmostEqual(p.quote[0], -horizon/12)

    def test_no_foresight_and_month_end_news_cannot_move_same_meeting(self):
        altered = list(self.months)
        t = 16  # May 2026, a meeting month
        altered[t] = replace(altered[t], purchases=altered[t].purchases+240, net=altered[t].net+240)
        before = self.scenario(self.months, self.central)
        after = self.scenario(altered, self.central)
        self.assertEqual(before[:t], after[:t])
        for field in ("policy_rate_gap_pp", "meeting_forecast_inflation_gap_12m_ahead_pp", "inflation_gap_pp"):
            self.assertEqual(before[t][field], after[t][field])
        self.assertLess(after[t]["no_purchases_gel_per_usd"], before[t]["no_purchases_gel_per_usd"])
        self.assertLess(after[t+1]["policy_rate_gap_pp"], before[t+1]["policy_rate_gap_pp"])

    def test_identical_policy_and_zero_pass_through(self):
        zero = replace(self.central, case=replace(self.central.case, impact=0))
        for r in self.scenario(self.months, zero):
            for modeled, observed in (("no_purchases_gel_per_usd","observed_gel_per_usd"),
                    ("no_purchases_yoy_inflation_pct","observed_yoy_inflation_pct"),
                    ("no_purchases_policy_rate_pct","observed_policy_rate_pct")):
                self.assertEqual(r[modeled], r[observed])
        no_prices = self.scenario(self.months, replace(self.central, target=0))
        for r in no_prices:
            self.assertEqual((r["inflation_gap_pp"], r["policy_rate_gap_pp"], r["parity_fx_gap_log_points"]), (0, 0, 0))

    def test_all_paths_stable_to_longer_forecast_tail_and_lag_shape(self):
        # All three state variables at every month-end, including the most persistent case.
        for s in model.SETTINGS:
            a, b = self.scenario(self.months, s), self.scenario(self.months, s, n=300)
            for t, m in enumerate(self.months):
                for col in ("no_purchases_gel_per_usd", "no_purchases_yoy_inflation_pct", "no_purchases_policy_rate_pct"):
                    self.assertLess(abs(a[t][col]-b[t][col]), 1e-9, (s.case.name, m.month, col))
        fast = replace(self.central, window=15)
        ref = self.intervals[:model.N]
        k = model.calibrate(ref, fast, self.b)
        self.assertAlmostEqual(model.unit_fx(ref, fast, k, self.b).inflation[24], -.25, places=9)
        # 100 bp controlled rate path, annual CPI domestic channel standalone.
        unit = [1.]
        for interval in ref[1:24]:
            unit.append(unit[-1] * .75 ** (interval/3))
        self.assertAlmostEqual(self.b * two_stage(unit, 24, 18), .4)

    def test_diminishing_response_forecasts_recover_both_states(self):
        s = replace(self.central, case=replace(self.central.case, response="diminishing"))
        rows = self.scenario(self.months, s)
        prior = [r for r in read(ROOT / "reports/r3_fixed_rate/sensitivities.csv")
                 if r["case"] == "diminishing_central"]
        for r, staged in zip(rows, prior, strict=True):
            direct = 100 * math.log(float(staged["without_purchases_gel_per_usd"])/float(staged["observed_gel_per_usd"]))
            self.assertAlmostEqual(r["direct_fx_gap_log_points"], direct, places=7)
            total = 100 * math.log(r["no_purchases_gel_per_usd"]/r["observed_gel_per_usd"])
            self.assertAlmostEqual(total - r["parity_fx_gap_log_points"], direct, places=7)


if __name__ == "__main__":
    unittest.main()
