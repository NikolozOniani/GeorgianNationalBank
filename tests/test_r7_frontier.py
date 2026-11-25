"""Replicate the published partial-policy results directly from upstream rows and the R3 solver."""
import csv
import math
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
import r3_policy_feedback as model

FRONTIER = ROOT/"reports/r7_frontier"
R7 = ROOT/"reports/r7_synthesis"


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


class FrontierTests(unittest.TestCase):
    def test_same_r3_solution_after_removing_only_the_omitted_purchases(self):
        months, gdp, history, weights, _ = model.fx.load_inputs()
        dates, prices = model.episode_calendar(months), model.headline()
        intervals = model.meeting_intervals(dates, model.N+len(months))
        demand = model.demand_coefficient(intervals[:model.N])
        rows = read(FRONTIER/"monthly.csv")
        # Directly solve each system on the smaller purchase shock. Common sales cancel in the difference.
        for gross, setting in zip((4000, 5000, 4500), model.SETTINGS, strict=True):
            target = [r for r in rows if float(r["target_september_gross_usdm"])==gross and r["fx_case"]==setting.case.name]
            self.assertEqual(len(target),21)
            s = float(target[0]["retained_share"])
            shocks = [replace(m,purchases=(1-s)*m.purchases,net=(1-s)*m.purchases-m.sales) for m in months]
            k = model.calibrate(intervals[:model.N],setting,demand)
            solved = model.episode(shocks,gdp,history,weights,prices,dates,intervals,setting,k,demand)
            for calculated, reference, source in zip(target,solved,months,strict=True):
                self.assertEqual(calculated["month"],source.month)
                self.assertAlmostEqual(float(calculated["gel_per_usd"]),reference["no_purchases_gel_per_usd"],places=7)
                self.assertAlmostEqual(float(calculated["policy_rate_pct"]),reference["no_purchases_policy_rate_pct"],places=7)
                self.assertEqual(float(calculated["common_sales_usdm"]),source.sales)

    def test_purchase_lots_interest_and_endpoints(self):
        months, *_ = model.fx.load_inputs()
        monthly = read(FRONTIER/"monthly.csv")
        fin = read(R7/"funding_accounts.csv")
        for policy in read(FRONTIER/"policies.csv"):
            rows = [r for r in monthly if (r["fx_case"],float(r["target_september_gross_usdm"])) ==
                    (policy["fx_case"],float(policy["september_gross_usdm"]))]
            self.assertEqual(len(rows),len(months))
            buys = [float(r["purchases_usdm"]) for r in rows]
            quotes = [float(r["gel_per_usd"]) for r in rows]
            gel_lots = [q*b for q,b in zip(quotes,buys,strict=True)]
            lots = [sum(buys[j]*math.prod(1+m.sofr/1200 for m in months[j+1:t]) for j in range(t)) for t in range(1,22)]
            funding = sum(sum(gel_lots[:t])*float(r["policy_rate_pct"])/2400 for t,r in enumerate(rows))
            earnings = sum(lots[t-1]*months[t].sofr*quotes[t]/1200 for t in range(1,21))
            self.assertAlmostEqual(float(rows[-1]["retained_lots_usdm"]),lots[-1],places=5)
            self.assertAlmostEqual(float(policy["net_interest_half_paid_gelm"]),funding-earnings,places=5)
            self.assertAlmostEqual(float(rows[-1]["gross_reserves_usdm"]),float(policy["september_gross_usdm"]),places=6)
            if float(policy["retained_share"])==1:
                self.assertEqual(quotes[-1],months[-1].quote)
                for basis,col in (("paid","net_interest_half_paid_gelm"),("displaced","net_interest_half_displaced_refi_gelm")):
                    prior = next(r for r in fin if r["fx_case"]==policy["fx_case"] and r["rate_basis"]==basis
                               and float(r["remunerated_or_displaced_share"])==.5)
                    self.assertAlmostEqual(float(policy[col]),float(prior["interest_only_cost_gelm"]),places=6)
            if float(policy["retained_share"])==0:
                self.assertEqual(sum(buys),0.)
                self.assertEqual(float(policy["financing_principal_gelm"]),0.)

    def test_liquidity_thresholds_and_rolling_shortfalls(self):
        stresses = read(R7/"reserve_stresses.csv")
        stocks = read(R7/"monthly_accounts.csv")
        end = next(r for r in stocks if r["month"]=="2026-09" and r["fx_case"]=="central")
        base, span = float(end["alternative_gross_usdm"]),float(end["closing_lot_usdm"])
        def gap(s, target):
            delta = (target-base)/span * (float(s["with_purchases_usdm"])-float(s["without_purchases_usdm"]))
            return max(0.,float(s["required_usable_usdm"])-float(s["without_purchases_usdm"])-delta)
        source = {(r["origin"],r["months"],r["stress"]):r for r in stresses}
        for r in read(FRONTIER/"coverage_thresholds.csv"):
            sept = source["2026-09",r["months"],r["stress"]]
            for column, candidates in (("september_min_gross_in_policy_family_usdm",[sept]),
                    ("september_gross_to_pass_all_origins_usdm",[s for s in stresses if (s["stress"],s["months"])==(r["stress"],r["months"])])):
                if r[column]:
                    target = float(r[column])
                    self.assertLess(max(gap(s,target) for s in candidates),1e-6)
                    if target>base+.001:
                        self.assertGreater(max(gap(s,target-.01) for s in candidates),1e-6)
                else:
                    self.assertGreater(max(gap(s,base+span) for s in candidates),1e-6)
        for r in read(FRONTIER/"rolling_protection.csv"):
            src = source[r["origin"],r["months"],r["stress"]]
            low,high = [gap(src,float(r[k])) for k in ("from_september_gross_usdm","to_september_gross_usdm")]
            self.assertAlmostEqual(float(r["additional_shortfall_covered_usdm"]),low-high,places=6)
        intervals = read(FRONTIER/"increments.csv")
        full = next(r for r in intervals if r["interval"]=="comparison" and float(r["from_gross_usdm"])<2300)
        for col in ("extra_buys_usdm","extra_net_interest_half_paid_gelm","scaled_sales_additional_protection_usdm"):
            self.assertAlmostEqual(sum(float(r[col]) for r in intervals if r["interval"]=="adjacent"),float(full[col]),places=6)

    def test_interval_insurance_hurdles_by_first_event_annuity(self):
        rows = read(FRONTIER/"insurance_hurdles.csv")
        monthly = [r for r in read(R7/"monthly_accounts.csv") if r["fx_case"]=="central"]
        conversions = [float(r["without_purchases_quote"])/(float(r["observed_cpi_dec2024_1"])*
                       float(r["cpi_level_ratio_without_to_observed"])*1.03**(t/12)) for t,r in enumerate(monthly,1)]
        lot = float(monthly[-1]["closing_lot_usdm"])
        converter = conversions[-1]
        exposure = sum(float(r["closing_lot_usdm"])*v/12 for r,v in zip(monthly[:-1],conversions[1:],strict=True))
        exposure += lot*converter*(1-1.03**-5)/.03
        def first_event_loss(p):
            return 3810*p/(p+.03)*(1-((1-p)/1.03)**5)
        for r in rows:
            extra = float(r["to_gross_usdm"])-float(r["from_gross_usdm"])
            cost = .01*float(r["alternative_net_spread_pct"])*exposure*extra/lot
            self.assertAlmostEqual(float(r["resource_cost_pv_dec2024_gelm"]),cost,places=5)
            p = float(r["lower_policy_assumed_annual_hazard_pct"])/100
            if r["break_even_hazard_reduction_pp"]:
                cut = float(r["break_even_hazard_reduction_pp"])/100
                self.assertAlmostEqual((first_event_loss(p)-first_event_loss(p-cut))*converter,cost,places=5)
            else:
                self.assertLess(first_event_loss(p)*converter,cost)


if __name__=="__main__":
    unittest.main()
