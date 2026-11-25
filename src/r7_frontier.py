"""September gross-reserve and monthly purchase policies on the completed linear R7 paths."""
import argparse
import hashlib
import math

from r7_synthesis import CASES, ROOT, as_csv, csvrows, required_reduction

PARENT = ROOT / "reports/r7_synthesis"
OUT = ROOT / "reports/r7_frontier"
LOCKS = {
    "monthly_accounts.csv": "d856034ddf5d2073aa50a1a62be001e7af46dd7eddce0a6b465d70d588e13d2d",
    "reserve_stresses.csv": "21111e7d1c8941af6cf0f294b720826ebbd1cc3876b17fdcbf37303c2e53d4de",
    "resource_frontier.csv": "6a393bae5663cb8ec0a7e658e812b611568d61dea8ae39cec1ca2410209653fe",
}
SELECTED = ("public_float", "unscaled_sales", "scaled_sales", "sales_bank100",
            "one_pct_floor", "five_pct_security_haircut", "deposits_only")
HORIZON = 12


def load():
    for name, digest in LOCKS.items():
        if hashlib.sha256((PARENT / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"R7 input vintage changed: {name}")
    monthly = csvrows(PARENT / "monthly_accounts.csv")
    paths = {case: [r for r in monthly if r["fx_case"] == case] for case in CASES}
    stresses = csvrows(PARENT / "reserve_stresses.csv")
    return paths, stresses


def path(source, share):
    """Price purchases retained in each policy's own economy. USD lower-bound sales stay common."""
    principal = holdings = paid = earned = displaced = 0.
    rows = []
    for r in source:
        observed = float(r["observed_quote"])
        no_buy = float(r["without_purchases_quote"])
        quote = observed * (no_buy / observed) ** (1 - share)
        observed_rate = float(r["observed_policy_pct"])
        no_buy_rate = float(r["alternative_policy_pct"])
        rate = no_buy_rate + share * (observed_rate - no_buy_rate)
        yield_pct = float(r["sofr_pct"])
        purchases = share * float(r["min_purchases_removed_usdm"])
        interest = holdings * yield_pct / 1200
        paid += principal * rate / 1200
        displaced += principal * no_buy_rate / 1200
        earned += interest * quote
        holdings += interest + purchases
        principal += quote * purchases
        gross = float(r["alternative_gross_usdm"]) + holdings
        liquid = float(r["alternative_fx_at_par_usdm"]) + holdings
        if min(gross, liquid) < 0 or abs(holdings-share*float(r["closing_lot_usdm"])) > .00001:
            raise ValueError(f"Reserve lots or feasible resources disagree in {r['month']}")
        rows.append(dict(month=r["month"], fx_case=r["fx_case"], retained_share=share,
                         purchases_usdm=purchases, common_sales_usdm=float(r["retained_sales_usdm"]),
                         gross_reserves_usdm=gross, liquid_fx_usdm=liquid, gel_per_usd=quote,
                         policy_rate_pct=rate, retained_lots_usdm=holdings, funding_principal_gelm=principal,
                         cumulative_full_paid_gelm=paid, cumulative_full_displaced_refi_gelm=displaced,
                         cumulative_reserve_income_gelm=earned))
    return rows


def gap(stress, share):
    low = float(stress["without_purchases_usdm"])
    available = low + share * (float(stress["with_purchases_usdm"]) - low)
    return max(0., float(stress["required_usable_usdm"]) - available)


def sufficient(stress):
    if gap(stress, 0) == 0:
        return 0.
    if gap(stress, 1) > 0:
        return None
    return gap(stress, 0) / (float(stress["with_purchases_usdm"])-float(stress["without_purchases_usdm"]))


def build():
    paths, stresses = load()
    central = paths["central"]
    end = central[-1]
    bottom, top = (float(end[k]) for k in ("alternative_gross_usdm", "actual_gross_usdm"))
    stock_span = top-bottom
    purchases = sum(float(r["min_purchases_removed_usdm"]) for r in central)
    terminal = [s for s in stresses if s["origin"] == end["month"]]
    thresholds = []
    for s in terminal:
        peers = [p for p in stresses if (p["months"],p["stress"]) == (s["months"],s["stress"])]
        shares = [sufficient(p) for p in peers]
        share = sufficient(s)
        attainable = all(x is not None for x in shares)
        worst = max(shares) if attainable else None
        binding = [p["origin"] for p,x in zip(peers,shares,strict=True)
                   if x == worst and (worst is None or worst > 0)]
        thresholds.append(dict(stress=s["stress"],months=int(s["months"]),
            september_usable_required_usdm=float(s["required_usable_usdm"]),
            september_usable_at_no_purchases_usdm=float(s["without_purchases_usdm"]),
            september_usable_at_full_purchases_usdm=float(s["with_purchases_usdm"]),
            september_min_retained_share=share,
            september_min_gross_in_policy_family_usdm=bottom+share*stock_span if share is not None else None,
            september_gap_at_full_usdm=gap(s,1), all_origins_min_retained_share=worst,
            september_gross_to_pass_all_origins_usdm=bottom+worst*stock_span if attainable else None,
            binding_or_infeasible_origins="|".join(binding)))
    by_stress = {s["stress"]:s for s in terminal if int(s["months"]) == HORIZON}
    peaks = [p["september_min_gross_in_policy_family_usdm"] for p in thresholds
             if p["months"] == HORIZON and p["september_min_retained_share"] is not None]
    targets = {bottom, top, *range(2500, 8001, 500), *range(4000,5001,100), *peaks}
    targets.update(bottom+stock_span*s for s in (.25,.5,.75))
    targets.update(bottom+stock_span*p/purchases for p in (4000,5000))
    grid = sorted(x for x in targets if bottom <= x <= top)
    resource = next(r for r in csvrows(PARENT/"resource_frontier.csv") if r["fx_case"]=="central"
                    and int(r["years_after_sep2026"])==5 and float(r["real_discount_pct"])==3
                    and float(r["loss_gdp_share"])==.1 and float(r["assumed_annual_hazard_reduction_pp"])==0)
    # A common no-purchase real exchange rate values external USD in every comparison (R7).
    full_hurdle = .01*float(resource["window_plus_continuation_exposure_pv_dec24_gelm_years"])
    conversion = float(end["without_purchases_quote"])/(float(end["observed_cpi_dec2024_1"])
                 *float(end["cpi_level_ratio_without_to_observed"])*1.03**(len(central)/12))
    initial_loss = .1*38100  # R7 loss = 10% of the rounded 2025 GDP benchmark in USDm
    monthly, frontier, levels = [], [], {}
    for gross in grid:
        share = (gross-bottom)/stock_span
        for case in CASES:
            rows = path(paths[case],share)
            monthly.extend(dict(target_september_gross_usdm=gross, **r) for r in rows)
            last = rows[-1]
            earned, funded = last["cumulative_reserve_income_gelm"], last["cumulative_full_paid_gelm"]
            out = dict(september_gross_usdm=gross, fx_case=case, retained_share=share,
                cumulative_gross_buys_usdm=purchases*share, liquid_fx_at_par_usdm=last["liquid_fx_usdm"],
                gel_per_usd=last["gel_per_usd"], more_usd_per_gel_vs_observed_pct=100*(float(end["observed_quote"])/last["gel_per_usd"]-1),
                policy_rate_pct=last["policy_rate_pct"], financing_principal_gelm=last["funding_principal_gelm"],
                funding_expense_half_paid_gelm=.5*funded, reserve_income_proxy_gelm=earned,
                net_interest_zero_paid_gelm=-earned, net_interest_half_paid_gelm=.5*funded-earned,
                net_interest_full_paid_gelm=funded-earned,
                net_interest_half_displaced_refi_gelm=.5*last["cumulative_full_displaced_refi_gelm"]-earned,
                annual_forward_half_paid_net_cost_usdm=last["retained_lots_usdm"]*(.5*last["policy_rate_pct"]-float(end["sofr_pct"]))/100)
            for name in SELECTED:
                out[name+"_gap_usdm"] = gap(by_stress[name],share)
            frontier.append(out)
            if case == "central":
                levels[gross] = out
    # The adjacent intervals are additive. Named comparisons may overlap those intervals.
    intervals = [(a,b,"adjacent") for a,b in zip(grid,grid[1:])]
    intervals.extend((a,b,"comparison") for a,b in ((bottom,top),(4000,5000),(4000,top),(5000,top),(5000,6000),(6000,top)))
    marginal, welfare, rolling = [], [], []
    for a,b,kind in intervals:
        low, high = levels[a], levels[b]
        extra = b-a
        def difference(key):
            return high[key] - low[key]
        row = dict(interval=kind, from_gross_usdm=a, to_gross_usdm=b, extra_gross_usdm=extra,
                   extra_buys_usdm=difference("cumulative_gross_buys_usdm"),
                   low_gel_per_usd=low["gel_per_usd"], high_gel_per_usd=high["gel_per_usd"],
                   fewer_usd_per_gel_at_high_pct=100*(1-low["gel_per_usd"]/high["gel_per_usd"]),
                   extra_funding_expense_half_paid_gelm=difference("funding_expense_half_paid_gelm"),
                   extra_income_gelm=difference("reserve_income_proxy_gelm"),
                   extra_net_interest_zero_paid_gelm=difference("net_interest_zero_paid_gelm"),
                   extra_net_interest_full_paid_gelm=difference("net_interest_full_paid_gelm"),
                   break_even_remunerated_share=difference("reserve_income_proxy_gelm")/(2*difference("funding_expense_half_paid_gelm")),
                   extra_net_interest_half_paid_gelm=difference("net_interest_half_paid_gelm"),
                   extra_annual_forward_half_paid_cost_usdm=difference("annual_forward_half_paid_net_cost_usdm"))
        for name in SELECTED:
            row[name+"_additional_protection_usdm"] = max(0., -difference(name+"_gap_usdm"))
        marginal.append(row)
        if kind == "comparison":
            for stress in stresses:
                if int(stress["months"]) != HORIZON or stress["stress"] not in ("public_float", "scaled_sales", "sales_bank100", "deposits_only"):
                    continue
                low_gap = gap(stress,low["retained_share"])
                high_gap = gap(stress,high["retained_share"])
                rolling.append(dict(from_september_gross_usdm=a,to_september_gross_usdm=b,
                    origin=stress["origin"],stress=stress["stress"],months=HORIZON,
                    low_policy_shortfall_usdm=low_gap,high_policy_shortfall_usdm=high_gap,
                    additional_shortfall_covered_usdm=low_gap-high_gap))
        for spread in (.5,1.,2.):
            cost = full_hurdle*spread*extra/stock_span
            for hazard in (.05,.1,.2):
                cut = required_reduction(cost/conversion,initial_loss,hazard,5,.03)
                welfare.append(dict(interval=kind,from_gross_usdm=a,to_gross_usdm=b,
                    alternative_net_spread_pct=spread,resource_cost_pv_dec2024_gelm=cost,
                    lower_policy_assumed_annual_hazard_pct=100*hazard,break_even_hazard_reduction_pp=cut,
                    upper_policy_break_even_annual_hazard_pct=None if cut is None else 100*hazard-cut))
    return {"policies.csv":frontier,"monthly.csv":monthly,"increments.csv":marginal,
            "coverage_thresholds.csv":thresholds,"insurance_hurdles.csv":welfare,"rolling_protection.csv":rolling}


def figure(tables):
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    with plt.rc_context({"font.family":"DejaVu Sans","font.size":9,"svg.fonttype":"none",
                         "svg.hashsalt":"nbg-marginal-frontier","axes.spines.top":False,"axes.spines.right":False}):
        fig, axes = plt.subplots(1,3,figsize=(12,4.2),layout="constrained")
        policies = tables["policies.csv"]
        for case,color in zip(CASES,("#7393a3","#146859","#9e512b"),strict=True):
            rows = [r for r in policies if r["fx_case"]==case]
            axes[0].plot([r["september_gross_usdm"]/1000 for r in rows],[r["gel_per_usd"] for r in rows],
                         lw=2,color=color,label=case.capitalize())
        rows = [r for r in policies if r["fx_case"]=="central"]
        x = [r["september_gross_usdm"]/1000 for r in rows]
        for key,label in (("public_float","Public dues"),("scaled_sales","Plus scaled sales"),
                          ("sales_bank100","Plus sales and bank call"),("deposits_only","Sales, deposits only")):
            axes[1].plot(x,[r[key+"_gap_usdm"]/1000 for r in rows],label=label)
        for key,label in (("net_interest_zero_paid_gelm","0%"),("net_interest_half_paid_gelm","50%"),("net_interest_full_paid_gelm","100%")):
            axes[2].plot(x,[r[key] for r in rows],label=label)
        for ax,title,unit in zip(axes,("September exchange rate","Uncovered twelve-month stress","Episode net financing cost"),("GEL per USD","USD billion","GEL million"),strict=True):
            ax.set_title(title,loc="left",weight="bold",fontsize=11)
            ax.set_ylabel(unit)
            ax.set_xlabel("September gross reserves, USD billion")
            ax.axvspan(4,5,color="#cda93e",alpha=.17,zorder=0)
            ax.grid(axis="y",alpha=.17)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.legend(frameon=False,loc="best",fontsize=8)
        axes[2].get_legend().set_title("Remunerated share")
        axes[2].axhline(0,color="#444",linewidth=.6)
        fig.suptitle("Georgia’s reserve purchase choices, January 2025–September 2026",fontsize=14,weight="bold")
        stream=io.StringIO()
        fig.savefig(stream,format="svg",metadata={"Date":None,"Creator":"GeorgianNationalBank research"})
        plt.close(fig)
        return "\n".join(line.rstrip() for line in stream.getvalue().splitlines())+"\n"


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check",action="store_true")
    args = cli.parse_args()
    tables = build()
    files = {name:as_csv(rows) for name,rows in tables.items()}
    files["frontier.svg"] = figure(tables)
    for name, content in files.items():
        data = content.encode()
        if args.check:
            if (OUT/name).read_bytes() != data:
                raise SystemExit(f"{name} differs from the R7 frontier")
        else:
            (OUT/name).write_bytes(data)
    print("Verified" if args.check else "Generated", ", ".join(files))
