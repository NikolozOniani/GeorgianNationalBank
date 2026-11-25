"""Reviewer diagnostics for the 25 November research audit. All monetary inputs are millions."""
import argparse
import csv
import json
import math
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import r3_policy_feedback as model

BASE = "3033989257582a7a2a226a2e3e8569f964eb1017"
RESULT = ROOT / "reports/study_audit_2026_11_25/checks.json"
TARGET = 5000.


def read(path):
    with (ROOT / path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def close(actual, expected):
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=2e-6):
        raise ValueError(f"Reconciliation failed: {actual} versus {expected}")


def retained_purchases(months, carry, target_lots, order):
    """Fill the terminal lot budget with earliest or latest allowed buys, up to each month's cap."""
    quantities = [0.] * len(months)
    remaining = target_lots
    for i in order:
        take = min(months[i].purchases, remaining / carry[i])
        quantities[i] = take
        remaining = max(0., remaining - take * carry[i])
    close(remaining, 0.)
    return quantities


def replay(months, retained, source, parameters, stress):
    # R3 is linear in the purchase difference. Feed it the omitted impulse each month,
    # while leaving common sales, quotes at which gaps are anchored and starting stocks intact.
    difference = []
    for m, q in zip(months, retained, strict=True):
        if not 0 <= q <= m.purchases + 1e-9:
            raise ValueError("Purchase outside its observed monthly capacity")
        omitted = m.purchases - q
        difference.append(replace(m, purchases=omitted, net=omitted-m.sales))
    path = model.episode(difference, **parameters)
    lot = principal = paid = income = 0.
    failed_stresses = 0
    for m, q, p, original in zip(months, retained, path, source, strict=True):
        if not (m.month == p["month"] == original["month"]):
            raise ValueError("Policy and reserve accounting months disagree")
        quote = p["no_purchases_gel_per_usd"]
        interest = lot * m.sofr / 1200
        paid += .5 * principal * p["no_purchases_policy_rate_pct"] / 1200
        income += quote * interest
        principal += quote * q
        lot += interest + q
        close(p["conditional_gross_reserves_usdm"], float(original["alternative_gross_usdm"]) + lot)
        close(p["conditional_liquid_fx_usdm"], float(original["alternative_fx_at_par_usdm"]) + lot)
        if float(stress[m.month]["required_usable_usdm"]) > p["conditional_liquid_fx_usdm"] + 1e-7:
            failed_stresses += 1
    end = path[-1]
    close(end["conditional_gross_reserves_usdm"], TARGET)
    return {
        "retained_purchase_principal_usdm": sum(retained),
        "retained_lot_with_income_usdm": lot,
        "end_gross_usdm": end["conditional_gross_reserves_usdm"],
        "end_liquid_at_par_usdm": end["conditional_liquid_fx_usdm"],
        "end_gel_per_usd": end["no_purchases_gel_per_usd"],
        "end_usd_gain_per_gel_pct": end["higher_usd_per_lari_pct"],
        "episode_net_interest_cost_half_paid_gelm": paid - income,
        "episode_origins_with_uncovered_scaled_sales_of_21": failed_stresses,
        "min_liquid_at_par_usdm": min(p["conditional_liquid_fx_usdm"] for p in path),
        "first_buy": next(m.month for m,q in zip(months,retained,strict=True) if q>1e-7),
        "last_buy": next(m.month for m,q in reversed(list(zip(months,retained,strict=True))) if q>1e-7),
    }


def calculate():
    source = [r for r in read("reports/r7_synthesis/monthly_accounts.csv") if r["fx_case"] == "central"]
    # Independently bridge the USD 5bn stock, including the return on purchases retained before September.
    months, gdp, history, weights, opening = model.fx.load_inputs()
    end = months[-1]
    carry = [math.prod(1 + m.sofr / 1200 for m in months[i+1:]) for i in range(len(months))]
    full_lot = sum(m.purchases * factor for m,factor in zip(months, carry, strict=True))
    floor_gross = end.gross_reserves - full_lot
    target_lots = TARGET - floor_gross
    share = target_lots / full_lot
    if not 0. < share < 1.:
        raise ValueError("Reviewer target outside the interior of the R7 policy range")
    dates = model.episode_calendar(months)
    iv = model.meeting_intervals(dates, model.N + len(months))
    setting = model.SETTINGS[1]
    b = model.demand_coefficient(iv[:model.N])
    parameters = dict(gdp=gdp, history=history,weights=weights,prices=model.headline(),
                      dates=dates,intervals=iv,s=setting,k=model.calibrate(iv[:model.N],setting,b),b=b)
    stresses = read("reports/r7_synthesis/reserve_stresses.csv")
    sales = {r["origin"]:r for r in stresses if r["stress"]=="scaled_sales" and r["months"]=="12"}
    schedules = {
        "earliest_available_buys": retained_purchases(months, carry, target_lots, range(len(months))),
        "published_proportional": [m.purchases*share for m in months],
        "latest_available_buys": retained_purchases(months, carry, target_lots, reversed(range(len(months)))),
    }
    timings = {k:replay(months,v,source,parameters,sales) for k,v in schedules.items()}
    published = next(r for r in read("reports/r7_frontier/policies.csv")
                     if float(r["september_gross_usdm"]) == TARGET and r["fx_case"]=="central")
    prop = timings["published_proportional"]
    close(prop["end_gel_per_usd"],float(published["gel_per_usd"]))
    close(prop["episode_net_interest_cost_half_paid_gelm"],float(published["net_interest_half_paid_gelm"]))

    # Rebuild availability from raw-derived portfolio components; solve the two R7 stresses together.
    asset = next(r for r in read("reports/reserve_buffer_policy/opening_assets.csv") if r["date"] == "2026-09-30")
    cash, bonds, other = (float(asset[k]) for k in ("deposits","securities","other"))
    usable_ratio = (cash + .95*bonds)/(cash+bonds)
    eligible_at_full = cash + .95*bonds + min(0.,other)
    eligible_at_target = eligible_at_full - (end.gross_reserves-TARGET)*usable_ratio
    need = float(sales[end.month]["required_usable_usdm"])
    floor_with_both = end.gross_reserves - (eligible_at_full-need-100.)/usable_ratio
    alone = end.gross_reserves - (eligible_at_full-need)/usable_ratio
    prior = next(r for r in read("reports/r7_frontier/coverage_thresholds.csv")
                 if r["stress"]=="five_pct_security_haircut" and r["months"]=="12")
    close(alone,float(prior["september_min_gross_in_policy_family_usdm"]))

    return {"audited_commit":BASE, "recorded_opening_gel_per_usd":opening,
            "recorded_closing_gel_per_usd":end.quote,
            "observed_usd_gain_per_gel_pct":100*(opening/end.quote-1),
            "episode_net_usdm":sum(m.net for m in months),
            "minimum_buys_usdm":sum(m.purchases for m in months),
            "minimum_sales_usdm":sum(m.sales for m in months),
            "same_terminal_gross_different_timing":timings,
            "joint_september_sales_haircut_bank_call":{
                "public_plus_scaled_sales_need_usdm":need,
                "available_at_5000_gross_after_haircut_usdm":eligible_at_target,
                "extra_uncovered_with_100_disjoint_call_usdm":max(0.,need+100.-eligible_at_target),
                "remaining_disjoint_call_capacity_after_haircut_at_5000_usdm":eligible_at_target-need,
                "gross_needed_with_haircut_only_usdm":alone,
                "gross_needed_with_haircut_and_bank_call_usdm":floor_with_both}}


def rounded(record):
    if isinstance(record, dict):
        return {k:rounded(v) for k,v in record.items()}
    return round(record, 7) if isinstance(record,float) else record


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    result=json.dumps(rounded(calculate()),indent=2,allow_nan=False)+"\n"
    if args.check:
        if RESULT.read_text() != result:
            raise SystemExit("Reviewer diagnostics differ from the recorded results")
        print("Reviewer diagnostics verified")
    else:
        print(result,end="")
