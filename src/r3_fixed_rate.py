"""Direct GEL/USD response to removing market purchases at a common policy-rate path."""
import argparse
import io
import math
from dataclasses import dataclass, replace
from statistics import fmean

from r1_accounts import END, ROOT, START, csvrows
from r3_reopen import csv_text

OUT = ROOT / "reports/r3_fixed_rate"
R1 = "reports/r1_2026_11_10/"
PANEL = "reports/r3_reopen_2026_11_16/model_panel.csv"
ASSETS = "reports/reserve_buffer_policy/opening_assets.csv"
KERNELS = "reports/r3_reopen_2026_11_16/external_kernels.csv"


@dataclass(frozen=True)
class Case:
    name: str
    impact: float
    half_life: int
    response: str = "linear"
    gdp_override: float | None = None
    extra_two_way_usdm: float = 0
    omit_sale_month: str | None = None


CONSERVATIVE = Case("conservative", 0.47825, 3)
CENTRAL = Case("central", 0.9565, 10)
AGGRESSIVE = Case("aggressive", 1.913, 20)
PRIMARY = (CONSERVATIVE, CENTRAL, AGGRESSIVE)
CASES = (
    *PRIMARY,
    replace(CENTRAL, name="zero_impact", impact=0),
    *(replace(c, name="diminishing_" + c.name, response="diminishing") for c in PRIMARY),
    replace(CENTRAL, name="central_fast_decay", half_life=3),
    replace(CENTRAL, name="central_alternative_gdp", gdp_override=38100),
    replace(AGGRESSIVE, name="published_full_lags", response="published"),
    replace(CENTRAL, name="central_two_way", extra_two_way_usdm=10),
    replace(CENTRAL, name="central_no_march_sale", omit_sale_month="2026-03"),
)


@dataclass(frozen=True)
class Month:
    month: str
    quote: float
    policy_rate: float
    net: float
    purchases: float
    sales: float
    gross_reserves: float
    liquid_fx: float
    sofr: float
    gross_legs_unknown: bool


def load_inputs():
    panel = csvrows(ROOT / PANEL)
    months = [f"{year}-{month:02d}" for year in range(2020, 2027) for month in range(1, 13)]
    if [r["month"] for r in panel] != [m for m in months if m <= END]:
        raise ValueError("Monthly source coverage or ordering changed")
    bounds = csvrows(ROOT / R1 / "gross_flow_accounting_bounds.csv")
    episode = [r for r in panel if START <= r["month"] <= END]
    if [r["period"] for r in bounds] != [r["month"] for r in episode]:
        raise ValueError("R1 and exchange-rate months differ")
    gdp = next(float(r["gdp_current_usd"]) / 1e6 for r in
               csvrows(ROOT / "data/derived/r3_reopen_2026_11_16/gdp_observations.csv") if r["year"] == "2024")
    assets = {r["date"][:7]: r for r in csvrows(ROOT / ASSETS)}
    observations = []
    for r, b in zip(episode, bounds, strict=True):
        m = r["month"]
        net = float(b["net_market_purchases_usdm"])
        buys = float(b["gross_market_purchases_lower_bound_usdm"])
        sells = float(b["gross_market_sales_lower_bound_usdm"])
        if min(buys, sells) < 0 or not math.isclose(buys - sells, net, abs_tol=1e-8):
            raise ValueError(f"R1 gross legs disagree with net in {m}")
        if net != float(r["net_purchases_usdm"]) or gdp != float(r["gdp_normalization_usdm"]):
            raise ValueError(f"Panel disagrees with observed net flow or frozen GDP in {m}")
        observations.append(Month(
            m, float(r["gel_per_usd"]), float(r["policy_rate_pct"]), net, buys, sells,
            float(r["reserves_usdm"]), float(assets[m]["fx_at_par_conditional"]), float(r["sofr_mean_pct"]),
            not b["gross_market_purchases_upper_bound_usdm"] and not b["gross_market_sales_upper_bound_usdm"],
        ))
    pre = [r for r in panel if r["month"] < START]
    history = [100 * float(r["net_purchases_usdm"]) / float(r["gdp_normalization_usdm"]) for r in pre]
    kernel = [r for r in csvrows(ROOT / KERNELS) if r["spec"] == "A11_col4"][:len(episode)]
    if [int(r["month_after_impulse"]) for r in kernel] != list(range(len(episode))):
        raise ValueError("Missing or misordered Table A11 impulse weights")
    weights = [float(r["log_quote_pct_response_to_1pct_gdp"]) for r in kernel]
    return observations, gdp, history, weights, float(pre[-1]["gel_per_usd"])


def historical_exposure(flows_pct_gdp, decay):
    """Closing signed exposure and largest absolute exposure from a common zero start."""
    state = limit = 0.0
    for flow in flows_pct_gdp:
        state = decay * state + flow
        limit = max(limit, abs(state))
    return state, max(1.0, limit)


def diminishing(state, limit):
    """Unit slope through the historical scale, then marginal slope limit / abs(state)."""
    size = abs(state)
    if size <= limit:
        return state
    return math.copysign(limit * (1 + math.log(size / limit)), state)


def simulate(case, months, gdp, history, published_weights):
    gdp = case.gdp_override or gdp
    decay = 2 ** (-1 / case.half_life)
    actual, limit = historical_exposure(history, decay)
    alternative = actual
    flows_difference = []
    reserve_difference = 0.0
    first_failure = ""
    rows = []
    if case.response == "published" and len(published_weights) < len(months):
        raise ValueError("Published kernel does not cover the evaluation window")
    for m in months:
        hidden_pair = case.extra_two_way_usdm if m.gross_legs_unknown else 0.0
        purchases = m.purchases + hidden_pair
        sales = 0.0 if m.month == case.omit_sale_month else m.sales + hidden_pair
        actual_flow = 100 * m.net / gdp
        alternative_flow = -100 * sales / gdp
        actual = decay * actual + actual_flow
        alternative = decay * alternative + alternative_flow
        flows_difference.append(actual_flow - alternative_flow)
        if case.response == "diminishing":
            gap = case.impact * (diminishing(actual, limit) - diminishing(alternative, limit))
        elif case.response == "published":
            gap = sum(w * flow for w, flow in zip(published_weights, reversed(flows_difference)))
        else:
            gap = case.impact * (actual - alternative)

        # Missing USD lots earn the existing SOFR proxy starting the following month.
        reserve_difference = reserve_difference * (1 + m.sofr / 1200) + m.net + sales
        liquid_left = m.liquid_fx - reserve_difference
        gross_left = m.gross_reserves - reserve_difference
        if min(gross_left, liquid_left) < 0 and not first_failure:
            first_failure = m.month
        if not all(map(math.isfinite, (gap, gross_left, liquid_left, m.quote, m.policy_rate))) or m.quote <= 0:
            raise ValueError(f"Invalid input or calculated value in {m.month}")
        rows.append(dict(
            month=m.month, case=case.name, observed_gel_per_usd=m.quote,
            without_purchases_gel_per_usd=None if first_failure else m.quote * math.exp(-gap / 100),
            higher_usd_per_lari_pct=None if first_failure else 100 * math.expm1(gap / 100),
            purchases_removed_usdm=purchases, cf_sales_usdm=sales,
            conditional_gross_reserves_usdm=gross_left, conditional_liquid_fx_usdm=liquid_left,
            first_infeasible_month=first_failure,
        ))
    last = rows[-1]
    weakest = min(rows, key=lambda r: r["conditional_liquid_fx_usdm"])
    end_quote = last["without_purchases_gel_per_usd"]
    summary = dict(
        case=case.name, endpoint_month=last["month"], impact_log_points=case.impact,
        half_life_months=case.half_life if case.impact else None, gdp_scale_usdm=gdp,
        observed_gel_per_usd=last["observed_gel_per_usd"], without_purchases_gel_per_usd=end_quote,
        higher_usd_per_lari_pct=last["higher_usd_per_lari_pct"],
        lower_gel_per_usd_pct=None if first_failure else 100 * (1 - end_quote / last["observed_gel_per_usd"]),
        mean_monthly_higher_usd_per_lari_pct=None if first_failure else fmean(r["higher_usd_per_lari_pct"] for r in rows),
        purchases_removed_usdm=sum(r["purchases_removed_usdm"] for r in rows),
        cf_sales_usdm=sum(r["cf_sales_usdm"] for r in rows),
        diminishing_threshold_pct_gdp=limit if case.response == "diminishing" else None,
        min_conditional_liquid_fx_usdm=weakest["conditional_liquid_fx_usdm"], min_liquid_fx_month=weakest["month"],
        first_infeasible_month=first_failure,
    )
    return rows, summary


def chart(monthly, summaries, opening_quote):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"observed": "#273644", "conservative": "#3979a1", "central": "#047966", "aggressive": "#ac4f22"}
    labels = {"observed": "Observed", **{c.name: c.name.capitalize() for c in PRIMARY}}
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.fonttype": "none", "svg.hashsalt": "georgia-fixed-rates-v1",
                         "axes.spines.top": False, "axes.spines.right": False}):
        fig, (ax, dots) = plt.subplots(1, 2, figsize=(12, 5.0), gridspec_kw={"width_ratios": [2.25, 1]})
        fig.subplots_adjust(left=.075, right=.965, top=.75, bottom=.23, wspace=.32)
        x = range(len(monthly) + 1)
        for name, style in zip(colors, ("-", "-.", "-", "--"), strict=True):
            values = [opening_quote] + [r[name + "_gel_per_usd"] for r in monthly]
            ax.plot(x, values, color=colors[name], ls=style, lw=2.4 if name in ("central", "observed") else 1.8,
                    label=labels[name])
        ax.set_xticks([0, 3, 6, 9, 12, 15, 18, 21],
                      ["Dec 24", "Mar 25", "Jun", "Sep", "Dec", "Mar 26", "Jun", "Sep"])
        ax.set_ylabel("GEL per USD")
        ax.set_title("Month-end exchange rate", loc="left", fontsize=11, fontweight="bold")
        ax.legend(frameon=False, ncol=2, loc="lower left", fontsize=9)
        ax.grid(axis="y", alpha=.22)
        ax.set_axisbelow(True)

        for i, c in enumerate(PRIMARY):
            base = summaries[c.name]["higher_usd_per_lari_pct"]
            dim = summaries["diminishing_" + c.name]["higher_usd_per_lari_pct"]
            color = colors[c.name]
            dots.plot([dim, base], [i, i], color=color, lw=1.5)
            dots.scatter(dim, i, s=48, color="white", edgecolor=color, lw=1.8, zorder=3)
            dots.scatter(base, i, s=36, color=color, zorder=4)
        dots.set_yticks(range(3), [c.name.capitalize() for c in PRIMARY])
        dots.set_ylim(2.6, -.65)
        dots.set_xlim(left=0)
        dots.set_xlabel("Higher USD value per lari (%)")
        dots.set_title("September 2026 gap", loc="left", fontsize=11, fontweight="bold")
        dots.grid(axis="x", alpha=.22)
        dots.set_axisbelow(True)
        dots.scatter([], [], s=36, color="#374850", label="Linear")
        dots.scatter([], [], s=44, facecolors="white", edgecolor="#374850", label="Diminishing")
        dots.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(-.05, 1.0), fontsize=8)
        fig.suptitle("Georgia’s lari without NBG market purchases", x=.075, y=.97,
                     ha="left", fontsize=16, fontweight="bold")
        fig.text(.075, .868, "Conditional paths, January 2025–September 2026  |  Policy rates follow their observed path.",
                 color="#374850")
        fig.text(.075, .072, "Lower GEL/USD means a stronger lari. The zero-impact case coincides with the observed line.",
                 fontsize=9)
        fig.text(.075, .032, "NBG month-end quotes and R1 transaction ledger. Scenario differences depend on the assumed price response.",
                 fontsize=8, color="#47535C")
        buf = io.StringIO()
        fig.savefig(buf, format="svg", metadata={"Date": None, "Creator": "GeorgianNationalBank research"})
        plt.close(fig)
    return "\n".join(line.rstrip() for line in buf.getvalue().splitlines()) + "\n"


def outputs():
    months, gdp, history, weights, opening_quote = load_inputs()
    paths, endpoints = {}, {}
    for case in CASES:
        paths[case.name], endpoints[case.name] = simulate(case, months, gdp, history, weights)

    monthly = []
    for t, m in enumerate(months):
        row = dict(month=m.month, observed_gel_per_usd=m.quote, common_policy_rate_pct=m.policy_rate,
                   net_purchases_usdm=m.net, minimum_gross_purchases_removed_usdm=m.purchases,
                   retained_sales_usdm=m.sales)
        for c in PRIMARY:
            row[c.name + "_gel_per_usd"] = paths[c.name][t]["without_purchases_gel_per_usd"]
            row[c.name + "_higher_usd_per_lari_pct"] = paths[c.name][t]["higher_usd_per_lari_pct"]
        for field in ("conditional_gross_reserves_usdm", "conditional_liquid_fx_usdm", "first_infeasible_month"):
            row[field] = paths["central"][t][field]
        monthly.append(row)
    sensitivities = [row for c in CASES if c not in PRIMARY for row in paths[c.name]]
    return {"monthly.csv": csv_text(monthly), "sensitivities.csv": csv_text(sensitivities),
            "endpoints.csv": csv_text(list(endpoints.values())), "paths.svg": chart(monthly, endpoints, opening_quote)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare regenerated outputs with committed files")
    args = parser.parse_args()
    files = outputs()
    if not args.check:
        OUT.mkdir(exist_ok=True)
    for name, content in files.items():
        path = OUT / name
        if args.check:
            if path.read_bytes() != content.encode("utf-8"):
                raise SystemExit(f"Output differs: {path}")
        else:
            path.write_bytes(content.encode("utf-8"))
    print(f"{'Verified' if args.check else 'Wrote'} {len(files)} outputs in {OUT.relative_to(ROOT)}")
