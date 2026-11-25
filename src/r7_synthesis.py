"""Join the registered Georgian policy counterfactual, reserve accounts and conditional insurance."""
import argparse
import csv
import hashlib
import io
import json
import math
from statistics import fmean

import r7_liquidity as liquidity
from r1_accounts import ROOT, csvrows
from r3_fixed_rate import load_inputs
from r6_benefits import bond_price

OUT = ROOT / "reports/r7_synthesis"
FX = "reports/r3_policy_feedback/monthly.csv"
CPI = "data/derived/r3_policy_feedback/episode_headline_relatives.csv"
GROUPS = "reports/r5_2026_11_13/groups.csv"
CATEGORIES = "reports/r5_2026_11_13/category_exposures.csv"
FUNDING = "reports/r4_2026_11_12/monthly_exposures.csv"
BOND = "research/r6_bond_terms.json"
INSURANCE = "research/r6_assumptions.json"
AUDIT = "reports/r6_2026_11_15/audit_checks_2026_11_16.json"
CASES = ("conservative","central","aggressive")
INPUTS = (FX,CPI,GROUPS,CATEGORIES,FUNDING,BOND,INSURANCE,AUDIT,liquidity.ASSETS,liquidity.CALLS,
          liquidity.REPLAY,liquidity.TRADE,liquidity.ARA,"reports/reserve_buffer_policy/policy_matrix.csv",
          "reports/r6_2026_11_15/historical_sales_scale.csv","reports/r3_policy_feedback/sensitivities.csv",
          "reports/r3_reopen_2026_11_16/model_panel.csv","reports/r1_2026_11_10/gross_flow_accounting_bounds.csv",
          "data/derived/r3_reopen_2026_11_16/gdp_observations.csv","reports/r3_reopen_2026_11_16/external_kernels.csv")


def as_csv(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
    writer.writeheader()
    for row in rows:
        if any(isinstance(v,float) and not math.isfinite(v) for v in row.values()):
            raise ValueError("Nonfinite output")
        writer.writerow({k:round(v,9) if isinstance(v,float) else v for k,v in row.items()})
    return stream.getvalue()


def indexed(rows, key):
    result = {key(r):r for r in rows}
    if len(rows)!=len(result):
        raise ValueError("Duplicate input keys")
    return result


def accounts():
    months, _, _, _, opening_quote = load_inputs()
    paths = indexed(csvrows(ROOT/FX),lambda r:(r["month"],r["case"],r["policy"]))
    cpi = indexed(csvrows(ROOT/CPI),lambda r:r["month"])
    contracts = indexed(csvrows(ROOT/FUNDING),lambda r:r["month"])
    holdings = funding = pair_units = 0.
    base_price = 1.
    lots = {"2024-12":0.}
    rows, relative_prices = [], {}
    for t,m in enumerate(months,1):
        prior = holdings
        pair_units = pair_units*(1+m.sofr/1200) + int(m.gross_legs_unknown)
        earnings = prior*m.sofr/1200
        holdings += earnings+m.purchases
        lots[m.month] = holdings
        quote = m.quote
        old_funding = funding
        funding += quote*m.purchases
        base_price *= float(cpi[m.month]["previous_month_100"])/100
        for case in CASES:
            r = paths[m.month,case,"endogenous"]
            if abs(holdings-(m.gross_reserves-float(r["conditional_gross_reserves_usdm"])))>2e-6:
                raise ValueError("R3 reserve state does not reconcile")
            if abs(holdings-(m.liquid_fx-float(r["conditional_liquid_fx_usdm"])))>2e-6:
                raise ValueError("R3 liquid account does not reconcile")
            cf = float(r["no_purchases_gel_per_usd"])
            ratio = (100+float(r["no_purchases_yoy_inflation_pct"]))/(100+float(r["observed_yoy_inflation_pct"]))
            price = ratio * (relative_prices[case,t-12] if t>12 else 1.)
            relative_prices[case,t] = price
            alt_rate = float(r["no_purchases_policy_rate_pct"])
            rows.append(dict(month=m.month,fx_case=case,observed_quote=quote,without_purchases_quote=cf,
                usd_gain_per_lari_pct=100*(quote/cf-1),quote_decline_fraction=1-cf/quote,
                cpi_level_ratio_without_to_observed=price,annual_inflation_gap_pp=float(r["inflation_gap_pp"]),
                observed_policy_pct=m.policy_rate,alternative_policy_pct=alt_rate,
                min_purchases_removed_usdm=m.purchases,retained_sales_usdm=m.sales,
                actual_gross_usdm=m.gross_reserves,alternative_gross_usdm=m.gross_reserves-holdings,
                closing_lot_usdm=holdings,uniform_hidden_pair_at_zero_fx_floor_usdm=(m.liquid_fx-holdings)/pair_units if pair_units else None,
                actual_fx_at_par_usdm=m.liquid_fx,alternative_fx_at_par_usdm=m.liquid_fx-holdings,
                historical_funding_principal_gelm=funding,sofr_pct=m.sofr,usd_earnings_usdm=earnings,
                interest_at_receipt_gelm=earnings*quote,existing_lot_fx_revaluation_gelm=prior*(quote-opening_quote),
                full_remunerated_gelm=old_funding*m.policy_rate/1200,full_displaced_refi_gelm=old_funding*alt_rate/1200,
                all_listed_cd_interest_gelm=float(contracts[m.month]["cd_effective_interest_gelm"]),
                observed_cpi_dec2024_1=base_price))
        opening_quote=quote
    return rows,lots


def household(rows):
    groups = [r for r in csvrows(ROOT/GROUPS) if r["year"]=="2024"]
    cats = [r for r in csvrows(ROOT/CATEGORIES) if r["year"]=="2024"]
    out = []
    for r in rows:
        # All monthly central exposures plus terminal endpoints under every calibration.
        if r["fx_case"]!="central" and r["month"]!="2026-09":
            continue
        q, price_cut = r["quote_decline_fraction"], 1-r["cpi_level_ratio_without_to_observed"]
        for g in groups:
            matched = sum(float(s["survey_gel"]) for s in cats if (s["group"],s["level"])==(g["group"],g["level"]))
            if abs(.0025*matched-float(g["saving_025_survey_gel"]))>1e-6:
                raise ValueError("R5 matched category totals changed")
            remit = float(g["remittances_gel"])
            loss = remit*q
            out.append(dict(month=r["month"],fx_case=r["fx_case"],group=g["group"],level=g["level"],
                unmatched_consumption_pct=float(g["unmatched_pct"]),matched_survey_gel=matched,
                matched_saving_survey_gel=matched*price_cut,all_usd_receipts_loss_survey_gel=loss,
                net_two_channels_all_usd_survey_gel=matched*price_cut-loss,
                receipt_usd_fraction_at_break_even=matched*price_cut/loss if loss else None,
                matched_saving_dec2024_gel=float(g["matched_dec_gel"])*price_cut,
                matched_saving_dec2024_cluster_se=abs(price_cut/.0025)*float(g["saving_se"]),
                receipt_loss_survey_cluster_se=abs(q/.01)*float(g["loss_se"]),
                r5_quarter_pass_net_survey_gel=.25*q*matched-loss,
                r5_quarter_pass_net_cluster_se=abs(q/.01)*float(g["two_channel_se"])))
    return out


def financial(rows, share, rate_basis, discount):
    """PV of interest accruals versus PV of interest paid and a marked closing stock. Never add these two."""
    last = rows[-1]
    denom = [r["observed_cpi_dec2024_1"]*(1+discount)**(t/12) for t,r in enumerate(rows,1)]
    col = "full_remunerated_gelm" if rate_basis=="paid" else "full_displaced_refi_gelm"
    earned = sum(r["interest_at_receipt_gelm"] for r in rows)
    full = sum(r[col] for r in rows)
    full_pv = sum(r[col]/v for r,v in zip(rows,denom,strict=True))
    income_pv = sum(r["interest_at_receipt_gelm"]/v for r,v in zip(rows,denom,strict=True))
    mark = last["closing_lot_usdm"]*last["observed_quote"]-last["historical_funding_principal_gelm"]
    carry = share*full-earned
    revaluation = sum(r["existing_lot_fx_revaluation_gelm"] for r in rows)
    if abs(mark-earned-revaluation)>1e-5:
        raise ValueError("Incremental stock/income/FX bridge failed")
    return dict(fx_case=last["fx_case"],remunerated_or_displaced_share=share,rate_basis=rate_basis,discount_pct=100*discount,
        income_gelm=earned,funding_gelm=share*full,interest_only_cost_gelm=carry,
        break_even_funding_share_carry=earned/full,principal_fx_and_reinvested_income_revaluation_gelm=revaluation,
        terminal_asset_less_historical_principal_gelm=mark,marked_episode_cost_gelm=share*full-mark,
        break_even_closing_gel_per_usd=(last["historical_funding_principal_gelm"]+share*full)/last["closing_lot_usdm"],
        interest_only_cost_pv_dec24_gelm=share*full_pv-income_pv,
        marked_cost_pv_dec24_gelm=share*full_pv-mark/denom[-1],
        sep_usdm_to_pv_dec24_gelm=last["observed_quote"]/denom[-1],
        all_listed_cd_interest_gelm=sum(r["all_listed_cd_interest_gelm"] for r in rows))


def first_loss_pv(p, loss, years, d):
    """One first event at year end; subsequent crisis losses are in the first-event severity."""
    return sum(loss*p*(1-p)**(t-1)/(1+d)**t for t in range(1,years+1))


def required_reduction(cost, loss, p, years, d):
    if cost<=0:
        return 0.
    baseline=first_loss_pv(p,loss,years,d)
    if cost>baseline:
        return None
    lo,hi=0.,p
    for _ in range(60):
        mid=(lo+hi)/2
        if baseline-first_loss_pv(p-mid,loss,years,d)<cost:
            lo=mid
        else:
            hi=mid
    return 100*(lo+hi)/2


def continuation(rows, assumptions):
    last=rows[-1]
    lot=last["closing_lot_usdm"]
    # Central settings for one-at-a-time sensitivities, plus a fully crossed core grid.
    core = [(5,.03,s,a,.1,l,0.) for s in (0.,.5,1.) for a in (0.,.5,1.) for l in (.05,.1,.2)]
    axes = ([(n,.03,s,1.,.1,.1,0.) for n in (1,3,10) for s in (0.,.5,1.)]
            +[(5,d,s,1.,.1,.1,0.) for d in (0.,.05) for s in (0.,.5,1.)]
            +[(5,.03,s,1.,p,.1,0.) for p in (.05,.2) for s in (.5,1.)]
            +[(5,.03,s,1.,.1,.1,y) for y in (-1.,1.) for s in (.5,1.)])
    results=[]
    for years,d,share,alpha,p,severity,yshift in dict.fromkeys(core+axes):
        f=financial(rows,share,"paid",d)
        k=f["sep_usdm_to_pv_dec24_gelm"]
        loss=assumptions["gdp_usdm"]*severity
        hurdle=lot*(share*last["observed_policy_pct"]-last["sofr_pct"]-yshift)/100
        annuity=sum((1+d)**-t for t in range(1,years+1))
        prospective=hurdle*annuity
        total=f["marked_cost_pv_dec24_gelm"]/k+prospective
        resource=alpha*max(total,0.)
        baseline=first_loss_pv(p,loss,years,d)
        row=dict(years_after_sep2026=years,real_discount_pct=100*d,funding_share=share,
            positive_financial_cost_resource_share=alpha,no_purchase_annual_hazard_pct=100*p,loss_gdp_share=severity,
            yield_shift_pp=yshift,annual_forward_carry_cost_usdm=hurdle,prospective_cost_pv_sep26_usdm=prospective,
            full_window_financial_cost_pv_dec24_gelm=total*k,full_window_financial_cost_pv_sep26_equiv_usdm=total,
            pos_cost_resource_hurdle_sep26_usdm=resource,prospective_only_required_hazard_reduction_pp=
            required_reduction(alpha*max(prospective,0.),loss,p,years,d),
            full_window_required_hazard_reduction_pp=required_reduction(resource,loss,p,years,d),
            max_first_loss_benefit_pv_sep26_usdm=baseline,
            missing_pre_or_terminal_value_at_zero_insurance_pv_dec24_gelm=resource*k)
        for reduction in (0.,.01,.03,.05):
            saved=baseline-first_loss_pv(p-reduction,loss,years,d)
            row[f"net_scenario_value_at_{int(reduction*100)}pp_pv_dec24_gelm"]=(saved-resource)*k
        results.append(row)
    return results


def resource_frontier(monthly, assumptions):
    """Annual net external resource return that reserve insurance could offset; no domestic transfers."""
    out=[]
    for case in CASES:
        rows=[r for r in monthly if r["fx_case"]==case]
        for d in (0.,.03,.05):
            prior=exposure=0.
            for t,r in enumerate(rows,1):
                # Net forgone resources would accrue in the alternative economy.
                cf_price=r["observed_cpi_dec2024_1"]*r["cpi_level_ratio_without_to_observed"]
                conversion=r["without_purchases_quote"]/cf_price/(1+d)**(t/12)
                exposure += prior/12*conversion
                prior=r["closing_lot_usdm"]
            for n in (1,3,5,10):
                annuity=sum((1+d)**(-t) for t in range(1,n+1))
                full_exposure=exposure + conversion*prior*annuity
                for severity in (.05,.1,.2):
                    loss=severity*assumptions["gdp_usdm"]
                    p=.1
                    for cut in (0.,.01,.03):
                        benefit=(first_loss_pv(p,loss,n,d)-first_loss_pv(p-cut,loss,n,d))*conversion
                        out.append(dict(fx_case=case,years_after_sep2026=n,real_discount_pct=100*d,
                            baseline_annual_hazard_pct=100*p,assumed_annual_hazard_reduction_pp=100*cut,
                            loss_gdp_share=severity,window_exposure_pv_dec24_gelm_years=exposure,
                            window_plus_continuation_exposure_pv_dec24_gelm_years=full_exposure,
                            insurance_pv_dec24_gelm=benefit,break_even_external_return_spread_bps=10000*benefit/full_exposure,
                            net_value_at_100bps_pv_dec24_gelm=benefit-.01*full_exposure,
                            required_hazard_reduction_at_100bps_pp=required_reduction(
                                .01*full_exposure/conversion,loss,p,n,d)))
    return out


def bond_test(rows, settings):
    # Reuse only bond terms and assumptions independently checked against the two MoF PDFs.
    source=json.loads((ROOT/BOND).read_text())
    audit=json.loads((ROOT/AUDIT).read_text())["input_sha256"]
    for path in (BOND,INSURANCE):
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=audit[path]:
            raise ValueError("R6 audited source terms or configuration changed")
    prior=next(r for r in rows if r["month"]=="2025-12")
    ra,rn=prior["actual_gross_usdm"],prior["alternative_gross_usdm"]
    slope=settings["spread_slope"]*math.log((settings["gdp_usdm"]+ra)/(settings["gdp_usdm"]+rn))
    def proceeds(y):
        return bond_price(source["face_usdm"],source["coupon_pct"]/100,y,source["years"],source["payments_per_year"])
    y=source["yield_pct"]/100
    base=proceeds(y)
    if abs(base-source["face_usdm"]*source["price_pct"]/100)>.00251:
        raise ValueError("Reported issue price fails original terms")
    d=(1+y/source["payments_per_year"])**source["payments_per_year"]-1
    annuity=sum((1+d)**-t for t in range(1,1+source["years"]))
    lot=ra-rn
    r4 = next(r for r in csvrows(ROOT/"reports/r4_2026_11_12/conditional_carry.csv")
              if "CD" in r["mechanism"] and float(r["gel_per_usd_change_pct"])==0)
    u,f=float(r4["usd_return_proxy_pct"])/100,float(r4["gel_cost_pct"])/100
    rows=[]
    for transfer in (0.,.5,1.):
        gain=base-proceeds(y+slope*transfer)
        rows.append(dict(prior_stock_date=prior["month"],issue_date=source["settlement_date"],slope_transfer=transfer,
            counted_reserve_difference_usdm=lot,conditional_extra_yield_without_bps=10000*slope*transfer,
            proceeds_with_usdm=base,proceeds_without_usdm=base-gain,proceeds_benefit_usdm=gain,
            five_year_full_proxy_funding_cost_pv_usdm=lot*(f-u)*annuity,
            break_even_funding_share=(u+gain/(annuity*lot))/f))
    return rows


def build():
    settings=json.loads((ROOT/INSURANCE).read_text())
    monthly,lots=accounts()
    stress,tranches,ara=liquidity.run(lots)
    households=household(monthly)
    records={c:[r for r in monthly if r["fx_case"]==c] for c in CASES}
    fin=[financial(records[c],s,b,d) for c in CASES for b in ("paid","displaced")
         for s in (0.,.5,1.) for d in (0.,.03,.05)]
    forward=continuation(records["central"],settings)
    last=records["central"][-1]
    for row in tranches:
        horizon=row["months"]/12
        principal=row["tranche_principal_usdm"]
        service=row["marginal_shortfall_avoided_usdm"]
        event_probability=1-(1-.1)**horizon
        for label,share in (("zero",0.),("half",.5),("full",1.)):
            row[f"holding_cost_{label}_paid_usdm"]=principal*horizon*(share*last["observed_policy_pct"]-last["sofr_pct"])/100
        row["event_probability_over_horizon"]=event_probability
        row["loss_per_dollar_needed_half_paid"]=(
            max(row["holding_cost_half_paid_usdm"],0.)/(event_probability*service) if service>1e-8 else None)
    joint=[]
    for case in CASES:
        r=records[case][-1]
        f=financial(records[case],1.,"displaced",.03)
        for s in (v for v in stress if v["origin"]=="2026-09" and v["months"]==12 and v["stress"] in liquidity.PRIMARY):
            for share in (0.,.5,1.):
                # Counterfactual refinancing counterpart gives a case-specific opportunity rate.
                cost=r["closing_lot_usdm"]*(share*r["alternative_policy_pct"]-r["sofr_pct"])/100
                service=s["shortfall_avoided_usdm"]
                joint.append(dict(fx_case=case,insurance_case=s["stress"],displaced_refi_share=share,
                    end_observed_gel_per_usd=r["observed_quote"],end_without_gel_per_usd=r["without_purchases_quote"],
                    end_usd_gain_per_lari_pct=r["usd_gain_per_lari_pct"],mean_monthly_gain_pct=fmean(x["usd_gain_per_lari_pct"] for x in records[case]),
                    offsetting_no_purchase_premium_log_points=100*math.log(r["observed_quote"]/r["without_purchases_quote"]),
                    sep_cpi_level_reduction_pct=100*(1-r["cpi_level_ratio_without_to_observed"]),
                    window_interest_only_cost_gelm=share*f["funding_gelm"]-f["income_gelm"],
                    next_year_required_usable_usdm=s["required_usable_usdm"],next_year_shortfall_avoided_usdm=service,
                    next_year_carry_cost_usdm=cost,next_year_share_at_zero_carry=r["sofr_pct"]/r["alternative_policy_pct"],
                    event_probability_at_1pct_replacement_cost= max(cost,0.)/(.01*service) if service else (0. if cost<=0 else None),
                    required_loss_per_shortfall_dollar_at_10pct=max(cost,0.)/(.1*service) if service else (0. if cost<=0 else None),
                    annual_hazard_cut_pp_at_loss_10pct_gdp=100*max(cost,0.)/(.1*settings["gdp_usdm"])))
    stresses={r["specification"]:r for r in csvrows(ROOT/"reports/r3_policy_feedback/sensitivities.csv")}
    signs=[dict(case=s,conditional_quote=float(r["no_purchases_gel_per_usd"]),usd_gain_pct=float(r["higher_usd_per_lari_pct"]),
                offsetting_premium_log_points=100*math.log(records["central"][-1]["observed_quote"]/float(r["no_purchases_gel_per_usd"])))
           for s,r in stresses.items()]
    # The registered linear joint system is homogeneous in purchase impact at fixed persistence.
    observed=records["central"][-1]["observed_quote"]
    gap=math.log(observed/records["central"][-1]["without_purchases_quote"])
    for multiplier in (.5,1.,2.):
        z=multiplier*gap
        signs.append(dict(case=f"central_impact_times_{multiplier:g}_other_parameters_fixed",
            conditional_quote=observed*math.exp(-z),usd_gain_pct=100*math.expm1(z),offsetting_premium_log_points=100*z))
    return {"joint_results.csv":joint,"resource_frontier.csv":resource_frontier(monthly,settings),"monthly_accounts.csv":monthly,"reserve_stresses.csv":stress,
            "historical_comparators.csv":liquidity.historical_comparators(stress),
            "september_tranches.csv":tranches,"ara_comparison.csv":ara,"household_incidence.csv":households,
            "funding_accounts.csv":fin,"insurance_break_even.csv":forward,"bond_channel.csv":bond_test(records["central"],settings),
            "fx_reversals.csv":signs}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    locks=json.loads((OUT/"input_hashes.json").read_text())
    expected=set(INPUTS)|{"reports/r4_2026_11_12/conditional_carry.csv"}
    if set(locks)!=expected or any(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()!=v for k,v in locks.items()):
        raise SystemExit("Input hashes differ from the R7 vintage")
    from r7_figure import figure
    tables=build()
    files={name:as_csv(rows) for name,rows in tables.items()}
    files["reserve_tradeoffs.svg"]=figure(tables)
    for name,contents in files.items():
        data=contents.encode()
        if args.check:
            if data!=(OUT/name).read_bytes():
                raise SystemExit(f"Output differs: {name}")
        else:
            (OUT/name).write_bytes(data)
    print("R7 numerical tables verified" if args.check else "R7 numerical tables generated")


if __name__=="__main__":
    main()
