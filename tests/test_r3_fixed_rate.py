"""Independent flow, quote, impulse, nonlinear response and reserve checks."""
import calendar
import csv
import json
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from statistics import fmean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import r3_fixed_rate as fx


def records(path):
    with (ROOT / path).open(newline="") as stream:
        return list(csv.DictReader(stream))


class FixedRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.months, cls.gdp, cls.history, cls.weights, _ = fx.load_inputs()

    def run_case(self, case, months=None):
        return fx.simulate(case, self.months if months is None else months,
                           self.gdp, self.history, self.weights)

    def test_official_quotes_and_instrument_legs(self):
        prices = {r["date"]: float(r["usd_gel"]) for r in
                  records("data/derived/episode_2026_11_09/official_fx_daily.csv")}
        legs = {r["month"]: r for r in records("data/derived/episode_2026_11_09/intervention_monthly.csv")}
        source = {r["month"]: r for r in records("reports/acquisition_2026_11_09/monthly_policy_panel.csv")}
        self.assertEqual(len(self.months), 21)
        for m in self.months:
            year, month = map(int, m.month.split("-"))
            last_day = calendar.monthrange(year, month)[1]
            self.assertEqual(m.quote, prices[f"{m.month}-{last_day:02d}"])
            self.assertEqual(m.policy_rate, float(source[m.month]["policy_rate_end_pct"]))
            r = legs[m.month]
            net_other = float(r["nonauction_net_purchases_usdm"])
            self.assertAlmostEqual(m.purchases, float(r["auction_purchases_usdm"]) + max(0, net_other))
            self.assertAlmostEqual(m.sales, float(r["auction_sales_usdm"]) + max(0, -net_other))
        self.assertAlmostEqual(sum(m.net for m in self.months), 5803.15)
        self.assertAlmostEqual(sum(m.purchases for m in self.months), 5819.35)
        self.assertAlmostEqual(sum(m.sales for m in self.months), 16.20)

    def test_all_primary_quotes_against_direct_lag_sum(self):
        for case, impact, half_life in zip(fx.PRIMARY, (.47825, .9565, 1.913), (3, 10, 20), strict=True):
            rows, result = self.run_case(case)
            gains = []
            for t, r in enumerate(rows):
                # Divide USD millions by annual GDP in USD millions, with log points converted back to logs.
                log_ratio = sum(impact * m.purchases / self.gdp * 0.5 ** ((t-j) / half_life)
                                for j, m in enumerate(self.months[:t+1]))
                expected = self.months[t].quote / math.exp(log_ratio)
                self.assertAlmostEqual(r["without_purchases_gel_per_usd"], expected, places=12)
                gains.append(100 * (self.months[t].quote / expected - 1))
                self.assertAlmostEqual(r["higher_usd_per_lari_pct"], gains[-1], places=10)
            self.assertAlmostEqual(result["mean_monthly_higher_usd_per_lari_pct"], fmean(gains))
            self.assertAlmostEqual(result["lower_gel_per_usd_pct"], 100 * (1 - math.exp(-log_ratio)))

    def test_exact_unit_impulse_half_life_and_common_sales(self):
        synthetic = [replace(m, purchases=0, sales=0, net=0) for m in self.months]
        synthetic[0] = replace(synthetic[0], purchases=self.gdp/100, net=self.gdp/100)
        synthetic[1] = replace(synthetic[1], sales=80, net=-80)
        for case in fx.PRIMARY:
            rows, _ = self.run_case(case, synthetic)
            for t, target in ((0, case.impact), (case.half_life, case.impact/2)):
                ratio = synthetic[t].quote / rows[t]["without_purchases_gel_per_usd"]
                self.assertAlmostEqual(100 * math.log(ratio), target)

    def test_null_and_identical_policies(self):
        zero, _ = self.run_case(replace(fx.CENTRAL, impact=0))
        self.assertEqual([r["without_purchases_gel_per_usd"] for r in zero], [m.quote for m in self.months])
        only_sales = [replace(m, purchases=0, net=-m.sales) for m in self.months]
        for c in (fx.CENTRAL, replace(fx.CENTRAL, response="diminishing")):
            identical, _ = self.run_case(c, only_sales)
            for m, row in zip(only_sales, identical, strict=True):
                self.assertEqual(row["without_purchases_gel_per_usd"], m.quote)
                self.assertEqual(row["conditional_liquid_fx_usdm"], m.liquid_fx)

    def test_diminishing_response_uses_only_preperiod_for_threshold(self):
        for c in fx.PRIMARY:
            rows, endpoint = self.run_case(replace(c, response="diminishing"))
            # Independent finite sums of the signed order histories in each world.
            def stock(series):
                return sum(q * .5 ** (h/c.half_life) for h, q in enumerate(reversed(series)))
            prior_peaks = [abs(stock(self.history[:j])) for j in range(1, len(self.history)+1)]
            k = max(1, *prior_peaks)
            self.assertAlmostEqual(endpoint["diminishing_threshold_pct_gdp"], k)
            def response(v):
                return math.copysign(k * (1 + math.log(abs(v)/k)), v) if abs(v) > k else v
            actual = self.history + [100*m.net/self.gdp for m in self.months]
            cf = self.history + [-100*m.sales/self.gdp for m in self.months]
            for t, r in enumerate(rows, len(self.history)+1):
                gap = c.impact * (response(stock(actual[:t])) - response(stock(cf[:t])))
                expected = r["observed_gel_per_usd"] * math.exp(-gap/100)
                self.assertAlmostEqual(r["without_purchases_gel_per_usd"], expected, places=11)
            linear, _ = self.run_case(c)
            self.assertLess(rows[-1]["higher_usd_per_lari_pct"], linear[-1]["higher_usd_per_lari_pct"])

    def test_published_kernel_against_original_coefficients(self):
        cfg = next(r for r in json.loads((ROOT/"research/r3_reopen_calibration.json").read_text())
                   if r["id"] == "A11_col4")
        rows, _ = self.run_case(replace(fx.AGGRESSIVE, response="published"))
        gap = 0.0
        for t, m in enumerate(self.months):
            addition = sum(b*100*self.months[t-j].purchases/self.gdp
                           for j, b in enumerate(cfg["b_gel_per_usd"]) if j <= t)
            gap = cfg["rho"] * gap + addition
            self.assertAlmostEqual(rows[t]["without_purchases_gel_per_usd"], m.quote * math.exp(-gap/100), places=9)

    def test_two_way_cash_bridge_and_failure_cutoff(self):
        extra = 10
        rows, end = self.run_case(replace(fx.CENTRAL, extra_two_way_usdm=extra))
        self.assertAlmostEqual(end["purchases_removed_usdm"] - end["cf_sales_usdm"], 5803.15)
        for t, r in enumerate(rows):
            removed_value = sum((m.purchases + extra) *
                                math.prod(1 + later.sofr/1200 for later in self.months[j+1:t+1])
                                for j, m in enumerate(self.months[:t+1]))
            self.assertAlmostEqual(r["conditional_liquid_fx_usdm"], self.months[t].liquid_fx - removed_value)
            self.assertAlmostEqual(r["conditional_gross_reserves_usdm"], self.months[t].gross_reserves - removed_value)
        changed = self.months.copy()
        changed[2] = replace(changed[2], liquid_fx=20)
        rows, end = self.run_case(fx.CENTRAL, changed)
        self.assertEqual(end["first_infeasible_month"], "2025-03")
        self.assertIsNotNone(rows[1]["without_purchases_gel_per_usd"])
        self.assertTrue(all(r["without_purchases_gel_per_usd"] is None for r in rows[2:]))
