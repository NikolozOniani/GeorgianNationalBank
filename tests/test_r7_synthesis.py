"""Independent numerical replication of R7 from released source rows (no R7 production imports)."""
import csv
import hashlib
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"reports/r7_synthesis"


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def amount(row, name):
    return float(row[name])


class SynthesisTests(unittest.TestCase):
    def test_sources_and_three_worlds(self):
        for path, expected in json.loads((OUT/"input_hashes.json").read_text()).items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected, path)
        original = {(r["month"],r["case"]):r for r in read(ROOT/"reports/r3_policy_feedback/monthly.csv")
                    if r["policy"]=="endogenous"}
        rows = read(OUT/"monthly_accounts.csv")
        self.assertEqual(len(rows),63)
        for r in rows:
            old=original[r["month"],r["fx_case"]]
            self.assertAlmostEqual(amount(r,"usd_gain_per_lari_pct"),amount(old,"higher_usd_per_lari_pct"),places=6)
            self.assertAlmostEqual(amount(r,"alternative_gross_usdm"),amount(old,"conditional_gross_reserves_usdm"),places=6)
            self.assertAlmostEqual(amount(r,"alternative_fx_at_par_usdm"),amount(old,"conditional_liquid_fx_usdm"),places=6)
        signs=read(OUT/"fx_reversals.csv")
        for r in signs:
            self.assertAlmostEqual(float(r["conditional_quote"])*math.exp(float(r["offsetting_premium_log_points"])/100),
                                   2.6051,places=7)
        self.assertTrue(any(float(r["usd_gain_pct"])<0 for r in signs))

    def test_lots_financial_costs_and_terminal_without_double_count(self):
        src=read(ROOT/"reports/r3_reopen_2026_11_16/model_panel.csv")[-21:]
        gross=read(ROOT/"reports/r1_2026_11_10/gross_flow_accounting_bounds.csv")
        cpi={r["month"]:float(r["previous_month_100"])/100 for r in read(ROOT/"data/derived/r3_policy_feedback/episode_headline_relatives.csv")}
        fx={(r["case"],r["month"]):float(r["no_purchases_policy_rate_pct"]) for r in
            read(ROOT/"reports/r3_policy_feedback/monthly.csv") if r["policy"]=="endogenous"}
        purchases=[float(r["gross_market_purchases_lower_bound_usdm"]) for r in gross]
        self.assertAlmostEqual(sum(purchases),5819.35)
        self.assertEqual([r["period"] for r in gross],[r["month"] for r in src])
        i=[float(r["sofr_mean_pct"])/1200 for r in src]
        e=[float(r["gel_per_usd"]) for r in src]
        lots=[sum(purchases[j]*math.prod(1+rate for rate in i[j+1:t+1]) for j in range(t+1)) for t in range(21)]
        principal=[sum(q*p for q,p in zip(e[:t+1],purchases[:t+1],strict=True)) for t in range(21)]
        income=sum(lots[t-1]*i[t]*e[t] for t in range(1,21))
        mark=lots[-1]*e[-1]-principal[-1]
        for row in read(OUT/"funding_accounts.csv"):
            share=amount(row,"remunerated_or_displaced_share")
            d=amount(row,"discount_pct")/100
            f=[float(r["policy_rate_pct"]) if row["rate_basis"]=="paid" else fx[row["fx_case"],r["month"]] for r in src]
            costs=[share*f[t]*(principal[t-1] if t else 0.)/1200 for t in range(21)]
            factors=[(1+d)**(-(t+1)/12)/math.prod(cpi[r["month"]] for r in src[:t+1]) for t in range(21)]
            self.assertAlmostEqual(amount(row,"interest_only_cost_gelm"),sum(costs)-income,places=6)
            self.assertAlmostEqual(amount(row,"marked_episode_cost_gelm"),sum(costs)-mark,places=6)
            self.assertAlmostEqual(amount(row,"marked_cost_pv_dec24_gelm"),
                                   sum(v*df for v,df in zip(costs,factors,strict=True))-mark*factors[-1],places=6)
            self.assertAlmostEqual(amount(row,"break_even_closing_gel_per_usd")*lots[-1],principal[-1]+sum(costs),places=5)

    def test_september_shortfalls_and_every_tranche(self):
        stress=read(OUT/"reserve_stresses.csv")
        sources=read(ROOT/"reports/reserve_buffer_policy/scheduled_calls.csv")
        dues={int(r["months"]):-float(r["II1_signed"]) for r in sources if r["date"]=="2026-09-30"}
        orig=read(ROOT/"data/derived/episode_2026_11_09/trade_monthly.csv")
        imports={r["date"][:7]:float(r["value_usdm"]) for r in orig if r["direction"].strip()=="Import"}
        scale=(imports["2026-07"]+imports["2026-08"])/(imports["2020-01"]+imports["2020-02"])
        net=[float(r["net_use"]) for r in read(ROOT/"reports/minimum_reserve_buffer/scenario_events.csv") if r["case"]=="2020_sales"]
        rate=next(r for r in read(ROOT/"reports/r3_reopen_2026_11_16/model_panel.csv") if r["month"]=="2026-09")
        for row in stress:
            low,high,req=[amount(row,k) for k in ("without_purchases_usdm","with_purchases_usdm","required_usable_usdm")]
            service=max(0,min(high-low,req-low))
            self.assertAlmostEqual(service,amount(row,"shortfall_avoided_usdm"),places=6)
            if row["origin"]!="2026-09" or row["stress"] not in ("scaled_sales","public_float","sales_bank100"):
                continue
            h=int(row["months"])
            need=dues[h]+(0. if row["stress"]=="public_float" else scale*sum(net[:h]))+(100 if row["stress"]=="sales_bank100" else 0)
            self.assertAlmostEqual(req,need,places=6)
            tr=[r for r in read(OUT/"september_tranches.csv") if r["months"]==row["months"] and r["stress"]==row["stress"]]
            self.assertEqual(len(tr),60)
            self.assertAlmostEqual(sum(amount(r,"marginal_shortfall_avoided_usdm") for r in tr),service,places=6)
            for r in tr:
                addition=amount(r,"cumulative_principal_above_no_purchases_usdm")
                self.assertAlmostEqual(amount(r,"remaining_shortfall_usdm"),max(0,req-low-addition),places=6)
                horizon_probability=-math.expm1(math.log(.9)*h/12)
                principal=amount(r,"tranche_principal_usdm")
                half_cost=principal*h*(.5*amount(rate,"policy_rate_pct")-amount(rate,"sofr_mean_pct"))/1200
                self.assertAlmostEqual(amount(r,"event_probability_over_horizon"),horizon_probability,places=8)
                self.assertAlmostEqual(amount(r,"holding_cost_half_paid_usdm"),half_cost,places=8)
                protection=amount(r,"marginal_shortfall_avoided_usdm")
                if protection>1e-8:
                    self.assertAlmostEqual(amount(r,"loss_per_dollar_needed_half_paid")*horizon_probability*protection,
                                           max(half_cost,0.),places=7)
                else:
                    self.assertEqual(r["loss_per_dollar_needed_half_paid"],"")
        late=next(r for r in stress if (r["origin"],r["months"],r["stress"])==("2026-09","12","scaled_sales"))
        early=next(r for r in stress if (r["origin"],r["months"],r["stress"])==("2026-09","12","early_public_dues"))
        self.assertEqual(late["first_breach_without_month"],"2027-02")
        self.assertEqual(early["first_breach_without_month"],"2027-01")
        self.assertEqual(late["shortfall_avoided_usdm"],early["shortfall_avoided_usdm"])

    def test_ara_missingness_and_historical_horizons(self):
        ara=read(OUT/"ara_comparison.csv")
        self.assertEqual(len(ara),44)
        self.assertEqual(len([r for r in ara if r["ara_denominator_usdm"]]),7)
        self.assertTrue(all(not r["observed_ara_pct"] for r in ara if r["month"]=="2026-09"))
        self.assertTrue(all(r["target_150_gross_usdm"]=="" or abs(amount(r,"target_150_gross_usdm")*
            amount(r,"fx_at_par_share_of_gross")-amount(r,"target_150_fx_at_par_usdm"))<1e-5 for r in ara))
        history=[r for r in read(OUT/"historical_comparators.csv") if r["origin"]=="2026-09"]
        self.assertEqual(sorted(r["months"] for r in history),["1","1","12","3","3"])
        spike=next(r for r in history if r["sales_window"]=="2024-08 to 2024-10")
        self.assertAlmostEqual(amount(spike,"extra_coverage_at_horizon_usdm"),233.047794895+656.6-684.777981446,places=6)

    def test_household_price_level_and_no_transfer_case(self):
        macro=read(ROOT/"reports/r3_policy_feedback/monthly.csv")
        original=read(ROOT/"reports/r5_2026_11_13/groups.csv")
        for row in read(OUT/"household_incidence.csv"):
            prices={r["month"]:r for r in macro if r["case"]==row["fx_case"] and r["policy"]=="endogenous"}
            group=next(r for r in original if (r["year"],r["group"],r["level"])==("2024",row["group"],row["level"]))
            now=prices[row["month"]]
            old=prices.get("2025"+row["month"][4:]) if row["month"][:4]=="2026" else None
            level=math.prod((100+amount(r,"no_purchases_yoy_inflation_pct"))/
                            (100+amount(r,"observed_yoy_inflation_pct")) for r in [now,old] if r)
            basket=amount(group,"consumption_gel")*(1-amount(group,"unmatched_pct")/100)
            loss=(1-amount(now,"no_purchases_gel_per_usd")/amount(now,"observed_gel_per_usd"))*amount(group,"remittances_gel")
            self.assertAlmostEqual(amount(row,"net_two_channels_all_usd_survey_gel"),basket*(1-level)-loss,places=6)
            if loss:
                self.assertAlmostEqual(amount(row,"receipt_usd_fraction_at_break_even")*loss,basket*(1-level),places=6)
            else:
                self.assertEqual(row["receipt_usd_fraction_at_break_even"],"")

    def test_financial_and_resource_thresholds_using_annuity_formula(self):
        def pv(p,d,n,loss):
            q=(1-p)/(1+d)
            return loss*p*n/(1+d) if q==1 else loss*p/(1+d)*(1-q**n)/(1-q)
        for row in read(OUT/"insurance_break_even.csv"):
            n=int(row["years_after_sep2026"])
            d,p,loss=amount(row,"real_discount_pct")/100,amount(row,"no_purchase_annual_hazard_pct")/100,38100*amount(row,"loss_gdp_share")
            required=row["full_window_required_hazard_reduction_pp"]
            hurdle=amount(row,"pos_cost_resource_hurdle_sep26_usdm")
            if not required:
                self.assertGreater(hurdle,pv(p,d,n,loss))
            else:
                self.assertAlmostEqual(pv(p,d,n,loss)-pv(p-float(required)/100,d,n,loss),hurdle,places=6)
        monthly=read(OUT/"monthly_accounts.csv")
        for row in read(OUT/"resource_frontier.csv"):
            n,d=int(row["years_after_sep2026"]),amount(row,"real_discount_pct")/100
            path=[r for r in monthly if r["fx_case"]==row["fx_case"]]
            disc=[amount(r,"without_purchases_quote")/(amount(r,"observed_cpi_dec2024_1")*
                  amount(r,"cpi_level_ratio_without_to_observed"))/(1+d)**((t+1)/12) for t,r in enumerate(path)]
            exposure=sum(amount(r,"closing_lot_usdm")*df/12 for r,df in zip(path[:-1],disc[1:],strict=True))
            annuity=(1-(1+d)**-n)/d if d else n
            exposure+=amount(path[-1],"closing_lot_usdm")*disc[-1]*annuity
            loss=38100*amount(row,"loss_gdp_share")
            saved=(pv(.1,d,n,loss)-pv(.1-amount(row,"assumed_annual_hazard_reduction_pp")/100,d,n,loss))*disc[-1]
            self.assertAlmostEqual(10000*saved/exposure,amount(row,"break_even_external_return_spread_bps"),places=5)
            self.assertLess(abs(saved-.01*exposure-amount(row,"net_value_at_100bps_pv_dec24_gelm")),1e-5)
            cut=amount(row,"required_hazard_reduction_at_100bps_pp")/100 if row["required_hazard_reduction_at_100bps_pp"] else None
            if cut is not None:
                self.assertLess(abs((pv(.1,d,n,loss)-pv(.1-cut,d,n,loss))*disc[-1]-.01*exposure),1e-5)
            else:
                self.assertLess(pv(.1,d,n,loss)*disc[-1],.01*exposure)

    def test_single_issue_pricing_and_units(self):
        rows=read(OUT/"bond_channel.csv")
        data=json.loads((ROOT/"research/r6_bond_terms.json").read_text())
        f,c,y=data["face_usdm"],data["coupon_pct"]/100,data["yield_pct"]/100
        def price(rate):
            disc=(1+rate/2)**-10
            return f*(disc+c/rate*(1-disc))
        for row in rows:
            self.assertEqual(row["prior_stock_date"],"2025-12")
            shift=amount(row,"conditional_extra_yield_without_bps")/1e4
            self.assertAlmostEqual(price(y)-price(y+shift),amount(row,"proceeds_benefit_usdm"),places=7)
        self.assertEqual(amount(rows[0],"proceeds_benefit_usdm"),0.)
        self.assertLess(amount(rows[-1],"proceeds_benefit_usdm"),amount(rows[-1],"five_year_full_proxy_funding_cost_pv_usdm"))


if __name__=="__main__":
    unittest.main()
