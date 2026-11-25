"""Paired NBG cash-coverage tests at each R7 origin. All monetary inputs are USD millions."""
from dataclasses import dataclass, replace
import math

from minimum_reserve_buffer import month_end
from r1_accounts import ROOT, csvrows

ASSETS = "reports/reserve_buffer_policy/opening_assets.csv"
CALLS = "reports/reserve_buffer_policy/scheduled_calls.csv"
REPLAY = "reports/minimum_reserve_buffer/scenario_events.csv"
TRADE = "data/derived/episode_2026_11_09/trade_monthly.csv"
ARA = "reports/r2_2026_11_11/ara_components.csv"
HORIZONS = (1, 3, 12)


@dataclass(frozen=True)
class Stress:
    name: str
    sales: str = "scaled"
    bank: float = 0.  # assumed disjoint, verified-eligible residual required for this stress
    haircut: float = 0.
    gold: bool = False
    outside: float = 0.  # share of positive public uses covered exactly when due
    early: bool = False
    floor: float = 0.  # share of observed gross; same dollar floor in both worlds
    deposits_only: bool = False


CENTRAL = Stress("scaled_sales")
CASES = (replace(CENTRAL, name="public_float", sales="none"), CENTRAL,
         replace(CENTRAL, name="sales_bank100", bank=100),
         replace(CENTRAL, name="public_gold_deliverable", sales="none", gold=True),
         replace(CENTRAL, name="public_half_paid_outside", sales="none", outside=.5),
         replace(CENTRAL, name="unscaled_sales", sales="nominal"),
         replace(CENTRAL, name="five_pct_security_haircut", haircut=.05),
         replace(CENTRAL, name="gold_deliverable", gold=True),
         replace(CENTRAL, name="half_public_paid_outside", outside=.5),
         replace(CENTRAL, name="early_public_dues", early=True),
         replace(CENTRAL, name="one_pct_floor", floor=.01),
         replace(CENTRAL, name="deposits_only", deposits_only=True))
PRIMARY = ("public_float", "scaled_sales", "sales_bank100")


def stock_pair(asset, lot, s):
    cash, securities = float(asset["deposits"]), float(asset["securities"])
    fraction = 0. if s.deposits_only else 1-s.haircut
    eligible = cash + fraction*securities + min(0., float(asset["other"]))
    if s.gold:
        eligible += float(asset["gold"])
    # With no instrument-specific lots, withdraw the same fraction of deposits and
    # securities in the alternative. Gold and signed other positions stay common.
    liquid_per_usd = (cash + fraction*securities)/(cash+securities)
    if not 0 <= lot <= cash+securities+1e-5:
        raise ValueError("Marginal FX lots exceed identified currency assets")
    return eligible, eligible-lot*liquid_per_usd, liquid_per_usd


def schedule(cumulative, tape, scale, s):
    """One event group per projected month; simultaneous claims do not get invented priority."""
    events = [dict() for _ in range(12)]
    prior = 0.
    for h, early in ((1, 1), (3, 2), (12, 4)):
        use = cumulative[h] - prior
        prior = cumulative[h]
        events[(early if s.early else h)-1]["public"] = use - s.outside*max(0., use)
    for i, sale in enumerate(tape):
        if s.sales != "none":
            events[i]["sales"] = sale * (scale if s.sales == "scaled" else 1.)
    if s.bank:
        events[0]["bank"] = s.bank
    return events


def breach(events, opening, floor):
    used = 0.
    if opening < floor-1e-7:
        return 0, "opening floor", floor-opening
    for t, group in enumerate(events, 1):
        used += sum(group.values())
        if used+floor > opening+1e-7:
            return t, "+".join(k for k, v in group.items() if v>0), used+floor-opening
    return None, "", 0.


def incidence(need, without, with_buys):
    return max(need-without, 0.) - max(need-with_buys, 0.)


def run(lots):
    stocks = {r["date"]:r for r in csvrows(ROOT/ASSETS) if r["date"][:7] in lots}
    buckets = {(r["date"],int(r["months"])):-float(r["II1_signed"]) for r in csvrows(ROOT/CALLS)
               if r["date"] in stocks}
    tape = [float(r["net_use"]) for r in csvrows(ROOT/REPLAY) if r["case"]=="2020_sales"]
    if len(tape)!=12 or abs(sum(tape)-980.472)>1e-5 or len(stocks)!=22 or len(buckets)!=66:
        raise ValueError("Opening stocks, maturity buckets or historical sales changed")
    imports = {r["date"][:7]: float(r["value_usdm"]) for r in csvrows(ROOT/TRADE)
               if r["direction"].strip()=="Import"}
    def lag_imports(date):
        return sum(imports[month_end(date,-i)[:7]] for i in (1,2))/2
    historic = lag_imports("2020-03-31")
    out, tranches, ara = [], [], []
    ratios = {(r["quarter"],r["money_series"]):r for r in csvrows(ROOT/ARA)}
    for date, asset in sorted(stocks.items()):
        month = date[:7]
        lot = lots[month]
        scale = lag_imports(date)/historic
        due = {h:buckets[date,h] for h in HORIZONS}
        for s in CASES:
            high, low, per_usd = stock_pair(asset,lot,s)
            floor = s.floor*float(asset["headline"])
            events = schedule(due, tape, scale, s)
            for h in HORIZONS:
                seq = events[:h]
                cum = [0.]
                for group in seq:
                    cum.append(cum[-1]+sum(group.values()))
                need = max(cum)+floor
                low_t, why, amount = breach(seq,low,floor)
                high_t, _, _ = breach(seq,high,floor)
                headroom = max(high-need,0.)
                # First USD100m cut (including a fractional final cut) that breaches the floor.
                cut = None
                if high_t is not None:
                    cut = 0.
                elif low_t is not None:
                    cut = min(lot,100*(math.floor(headroom/(100*per_usd)+1e-10)+1))
                t, group, missing = breach(seq,high-per_usd*cut,floor) if cut is not None else (None,"",0.)
                row = dict(origin=month, months=h, stress=s.name, prior_two_months_import_scale=scale,
                           reported_net_public_drains_usdm=due[h],
                           market_sales_budget_usdm=sum(e.get("sales",0) for e in seq),
                           floor_usdm=floor, required_usable_usdm=need, with_purchases_usdm=high,
                           without_purchases_usdm=low, usable_per_extra_usd=per_usd,
                           shortfall_with_usdm=max(need-high,0.), shortfall_without_usdm=max(need-low,0.),
                           shortfall_avoided_usdm=incidence(need,low,high),
                           extra_disjoint_call_capacity_without_usdm=max(low-need,0.),
                           extra_disjoint_call_capacity_with_usdm=headroom,
                           first_breach_without_month=month_end(date,low_t)[:7] if low_t is not None else "",
                           first_breach_without_group=why, first_gap_without_usdm=amount,
                           first_failing_cut_usdm=cut, first_failing_cut_month=month_end(date,t)[:7] if t is not None else "",
                           first_failing_cut_group=group, first_failing_cut_gap_usdm=missing)
                out.append(row)
                if month=="2026-09" and s.name in PRIMARY:
                    prev = low
                    for j in range(1,math.ceil(lot/100)+1):
                        principal = min(j*100,lot)
                        now = low+principal*per_usd
                        fail, cause, deficit = breach(seq,now,floor)
                        tranches.append(dict(origin=month,months=h,stress=s.name,increment_number=j,
                            cumulative_principal_above_no_purchases_usdm=principal,
                            tranche_principal_usdm=principal-100*(j-1), marginal_shortfall_avoided_usdm=incidence(need,prev,now),
                            remaining_shortfall_usdm=max(need-now,0.), first_breach_month=month_end(date,fail)[:7] if fail is not None else "",
                            first_breach_group=cause, first_gap_usdm=deficit))
                        prev = now
        gross = float(asset["headline"])
        q = int(month[-2:])
        for money in ("M2","M3"):
            r = ratios.get((f"{month[:4]}Q{q//3}", money)) if q%3==0 else None
            den = float(r["ara_usdm"]) if r else None
            if r and abs(float(r["gir_usdm"])-gross)>1e-5:
                raise ValueError("ARA numerator vintage mismatch")
            share = float(asset["fx_at_par_conditional"])/gross
            ara.append(dict(month=month,money=money,observed_gross_usdm=gross,
                without_purchases_gross_usdm=gross-lot,ara_denominator_usdm=den,
                observed_ara_pct=100*gross/den if den else None,
                without_purchases_static_ara_pct=100*(gross-lot)/den if den else None,
                fx_at_par_share_of_gross=share,target_145_gross_usdm=1.45*den if den else None,
                target_150_gross_usdm=1.5*den if den else None,target_145_fx_at_par_usdm=1.45*den*share if den else None,
                target_150_fx_at_par_usdm=1.5*den*share if den else None))
    return out, tranches, ara


def historical_comparators(stresses):
    """Independent horizon-specific balances; never concatenate different historical shocks."""
    maxima = csvrows(ROOT/"reports/r6_2026_11_15/historical_sales_scale.csv")
    registry = {r["id"]:r for r in csvrows(ROOT/"reports/reserve_buffer_policy/policy_matrix.csv")}
    scenarios = [(int(r["horizon_months"]),float(r["max_net_sales_usdm"]),r["start_month"]+" to "+r["end_month"])
                 for r in maxima]
    scenarios += [(1,float(registry["August FX sales"]["amount"]),"August 2008"),
                  (3,float(registry["2009Q1 sales"]["amount"]),"2009Q1")]
    rows = []
    for r in stresses:
        if r["stress"] != "public_float":
            continue
        for h, sales, window in scenarios:
            if h == r["months"]:
                need = r["reported_net_public_drains_usdm"] + sales
                low,high = r["without_purchases_usdm"],r["with_purchases_usdm"]
                rows.append(dict(origin=r["origin"],months=h,sales_window=window,nominal_sales_usdm=sales,
                    combined_net_use_at_horizon_usdm=need,shortfall_at_horizon_without_usdm=max(0.,need-low),
                    shortfall_at_horizon_with_usdm=max(0.,need-high),
                    extra_coverage_at_horizon_usdm=incidence(need,low,high)))
    return rows
