"""Monthly no-purchases FX, headline inflation and policy-rate paths under the November protocol."""
import argparse
from dataclasses import dataclass, replace
from functools import lru_cache
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import toeplitz
from scipy.optimize import brentq
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve

import r3_fixed_rate as fx
from r1_accounts import ROOT, csvrows
from r3_reopen import csv_text

OUT = ROOT / "reports/r3_policy_feedback"
CPI = ROOT / "data/derived/r3_policy_feedback/episode_headline_relatives.csv"
DECISIONS = ROOT / "archive/legacy/reports/nbg_policy_decisions_2008_onward.csv"
LOCKS = ROOT / "archive/legacy/reports/nbg_source_manifest.json"
N = 180  # forecast tail per news arrival; only the 21 registered month-ends are outcomes
FX_UNIT = -100 * math.log1p(.10)  # 10% more USD per GEL on impact


@dataclass(frozen=True)
class Setting:
    case: fx.Case
    phi: float
    target: float  # positive magnitude of the eight-quarter disinflation, pp
    window: int = 21  # length of each of the two price-adjustment stages, months
    parity: int = 12
    smoothing: float = .75


SETTINGS = tuple(Setting(c, phi, target) for c, phi, target in
                 zip(fx.PRIMARY, (1.1, 1.5, 2.0), (0., .25, .50), strict=True))
ROMAN = "I II III IV V VI VII VIII IX X XI XII".split()


def month_key(t):
    year, m = divmod(t, 12)
    return f"{2025 + year}-{m + 1:02d}"


def extract_cpi(workbook):
    """National Total, previous month = 100, directly from the existing pinned vintage."""
    from openpyxl import load_workbook
    if hashlib.sha256(workbook.read_bytes()).hexdigest() != json.loads(LOCKS.read_text())["group_cpi.xlsx"]["sha256"]:
        raise ValueError("Unexpected Geostat source hash")
    wb = load_workbook(workbook, read_only=True, data_only=True)
    try:
        title, _, years, months, total = list(wb["Georgia"].iter_rows(max_row=5, values_only=True))
        if "Previous month=100" not in title[0] or total[:3] != (None, None, "Total"):
            raise ValueError("Geostat series definition changed")
        rows = []
        for j in range(3, len(months)):
            if years[j] is not None:
                year = int(years[j])
            m = f"{year}-{ROMAN.index(months[j]) + 1:02d}"
            if month_key(-12) <= m <= fx.END:
                rows.append(dict(month=m, previous_month_100=float(total[j])))
    finally:
        wb.close()
    return csv_text(rows)


def headline():
    rows = csvrows(CPI)
    keys = [month_key(t) for t in range(-12, 21)]
    if [r["month"] for r in rows] != keys:
        raise ValueError("Missing, duplicate or unordered CPI month")
    gross = [float(r["previous_month_100"]) / 100 for r in rows]
    if not all(math.isfinite(x) and x > 0 for x in gross):
        raise ValueError("Invalid headline price relative")
    return {keys[t]: 100 * (math.prod(gross[t-11:t+1]) - 1) for t in range(11, len(keys))}


def episode_calendar(months):
    events = [r for r in csvrows(DECISIONS) if "2024-12" <= r["decision_date"][:7] <= fx.END]
    dates = {r["decision_date"][:7]: r["decision_date"] for r in events}
    if len(dates) != len(events) or any(r["decision_date"][:7] != r["effective_date"][:7] for r in events):
        raise ValueError("Decision timing requires finer-than-monthly aggregation")
    for m in months:
        rate = float(max((r for r in events if r["effective_date"][:7] <= m.month),
                         key=lambda r: r["effective_date"])["policy_rate_pct"])
        if rate != m.policy_rate:
            raise ValueError(f"Effective decision and month-end rate disagree in {m.month}")
    return dates


def meeting_intervals(dates, length):
    """Elapsed whole months per meeting. Beyond September repeat an eight-meeting schedule."""
    intervals = []
    last = -1  # December 2024 meeting
    for t in range(length):
        event = month_key(t) in dates if month_key(t) <= fx.END else t % 12 + 1 in (2, 3, 5, 6, 7, 9, 10, 12)
        intervals.append(t - last if event else 0)
        if event:
            last = t
    return np.array(intervals)


def lag_weights(window):
    # One stage delays 1..W months and the other 0..W-1, all equally weighted.
    stage = np.full(window, 1 / window)
    return np.r_[0., np.convolve(stage, stage)]


@lru_cache(maxsize=24)
def operators(n, window, parity):
    price = lag_weights(window)
    # Change over twelve months of the filtered FX level, with zero pre-news history.
    annual_fx = np.r_[price, np.zeros(12)] - np.r_[np.zeros(12), price]
    domestic = lag_weights(18)
    zero_leads = np.zeros(n)
    F, V = [toeplitz(np.pad(kernel, (0, n - len(kernel))), zero_leads)
            for kernel in (annual_fx, domestic)]
    # F times the forward rate-sum operator. Each annual pp-month contributes 1/12.
    FU = np.zeros_like(F)
    for lead in range(parity):
        FU[:, lead:] += F[:, :n-lead] / 12
    return F, FU, V


@dataclass
class Projection:
    quote: np.ndarray  # alternative minus observed, 100 log GEL/USD
    inflation: np.ndarray  # annual headline inflation differential, pp
    rate: np.ndarray  # annual policy rate differential, pp
    domestic: np.ndarray  # part of the inflation differential from the domestic rate channel


def project(direct, intervals, s, k, b, rate_shock=0., fixed=False):
    """Conditional response to one new information vintage, with no subsequent shocks."""
    n = len(direct)
    F, FU, V = operators(n, s.window, s.parity)
    imported_direct = k * np.einsum("ij,j->i", F, direct)
    rate = np.zeros(n)
    if not fixed:
        retain = s.smoothing ** (intervals / 3)
        # Month-end news cannot change a decision earlier that month; its effect on
        # expected future rates is already priced at this month-end.
        loading = s.phi * (1 - retain)
        loading[0] = 0
        matrix = np.eye(n) - np.diag(retain[1:], -1)
        matrix[:-12] += loading[:-12, None] * (k * FU[12:] + b * V[12:])
        rhs = np.zeros(n)
        rhs[:-12] = loading[:-12] * imported_direct[12:]
        rhs[0] += rate_shock
        rate = spsolve(csc_matrix(matrix), rhs)
    elif rate_shock:
        raise ValueError("A policy innovation needs a variable rate")
    # Finite-horizon closure sets subsequent gap forecasts to zero.
    total = np.r_[0., np.cumsum(np.r_[rate, np.zeros(s.parity)])]
    parity_gap = (total[s.parity:s.parity+n] - total[:n]) / 12
    quote = direct - parity_gap
    domestic = -b * np.einsum("ij,j->i", V, rate)
    inflation = k * np.einsum("ij,j->i", F, quote) + domestic
    return Projection(quote, inflation, rate, domestic)


def demand_coefficient(intervals):
    # Direct non-FX price effect of the normalized 100 bp tightening, before the
    # policy rule responds again to inflation (controlled rate-path calibration).
    unit = np.cumprod(.75 ** (intervals / 3))
    unit /= unit[0]
    return .4 / np.convolve(lag_weights(18), unit)[24]


def unit_fx(intervals, s, k, b):
    direct = -(2. ** (-np.arange(len(intervals)) / s.case.half_life))
    solution = project(direct, intervals, s, k, b)
    scale = FX_UNIT / solution.quote[0]
    return Projection(solution.quote * scale, solution.inflation * scale,
                      solution.rate * scale, solution.domestic * scale)


def calibrate(intervals, s, b):
    if not s.target:
        return 0.
    def error(k):
        return unit_fx(intervals, s, k, b).inflation[24] + s.target
    k = brentq(error, 0., 1., xtol=1e-13)
    if abs(error(k)) > 1e-9:
        raise ValueError("Eight-quarter joint-system calibration failed")
    return k


def direct_revisions(months, gdp, history, case, n):
    """Changes to the entire expected direct path when one month's ledger becomes known."""
    decay = 2 ** (-1 / case.half_life)
    horizon = decay ** np.arange(n)
    actual, limit = fx.historical_exposure(history, decay)
    alternative = actual
    def gap(a, z):
        if case.response == "linear":
            return case.impact * (z - a) * horizon
        if case.response != "diminishing":
            raise ValueError("Unsupported direct response")
        return case.impact * np.array([fx.diminishing(z * h, limit) - fx.diminishing(a * h, limit)
                                       for h in horizon])
    for m in months:
        actual *= decay
        alternative *= decay
        prior = gap(actual, alternative)
        actual += 100 * m.net / gdp
        alternative -= 100 * m.sales / gdp
        yield gap(actual, alternative) - prior


def episode(months, gdp, history, weights, prices, dates, intervals, s, k, b, fixed=False, n=N):
    """Superpose only the projections issued by this date; the MPC precedes current news."""
    count = len(months)
    quote, inflation, rate, domestic, forecast, parity = np.zeros((6, count))
    for start, direct in enumerate(direct_revisions(months, gdp, history, s.case, n)):
        sol = project(direct, intervals[start:start+n], s, k, b, fixed=fixed)
        length = count - start
        for acc, values in ((quote, sol.quote), (inflation, sol.inflation), (rate, sol.rate),
                            (domestic, sol.domestic), (parity, sol.quote - direct)):
            acc[start:] += values[:length]
        forecast[start+1:] += sol.inflation[13:length+12]
    benchmark, _ = fx.simulate(s.case, months, gdp, history, weights)
    rows = []
    for t, (m, ref) in enumerate(zip(months, benchmark, strict=True)):
        if ref["first_infeasible_month"]:
            raise ValueError(f"Infeasible reference USD settlement in {m.month}")
        direct = 100 * math.log(ref["without_purchases_gel_per_usd"] / m.quote)
        if abs(quote[t] - direct - parity[t]) > 1e-9:
            raise ValueError("Revisions do not recover the existing direct FX calculation")
        i = m.policy_rate + rate[t]
        y = prices[m.month] + inflation[t]
        if not (math.isfinite(i) and i >= 0 and y > -100 and math.isfinite(y)):
            raise ValueError(f"Infeasible rate or CPI in {m.month}")
        rows.append(dict(month=m.month, case=s.case.name, policy="fixed" if fixed else "endogenous",
                         mpc_decision_date=dates.get(m.month, ""), purchases_removed_usdm=m.purchases,
                         retained_sales_usdm=m.sales,
                         conditional_gross_reserves_usdm=ref["conditional_gross_reserves_usdm"],
                         conditional_liquid_fx_usdm=ref["conditional_liquid_fx_usdm"],
                         observed_gel_per_usd=m.quote, no_purchases_gel_per_usd=m.quote * math.exp(quote[t]/100),
                         higher_usd_per_lari_pct=100 * math.expm1(-quote[t]/100),
                         observed_yoy_inflation_pct=prices[m.month], no_purchases_yoy_inflation_pct=y,
                         inflation_gap_pp=inflation[t], observed_policy_rate_pct=m.policy_rate,
                         no_purchases_policy_rate_pct=i, policy_rate_gap_pp=rate[t],
                         meeting_forecast_inflation_gap_12m_ahead_pp=forecast[t] if m.month in dates else None,
                         direct_fx_gap_log_points=direct, parity_fx_gap_log_points=parity[t],
                         fx_inflation_gap_pp=inflation[t]-domestic[t], domestic_rate_inflation_gap_pp=domestic[t]))
    return rows


def summary(rows, label):
    end = rows[-1]
    return dict(specification=label, case=end["case"], policy=end["policy"], month=end["month"],
                **{col: end[col] for col in ("no_purchases_gel_per_usd", "higher_usd_per_lari_pct",
                    "no_purchases_yoy_inflation_pct", "inflation_gap_pp", "no_purchases_policy_rate_pct",
                    "policy_rate_gap_pp", "parity_fx_gap_log_points")},
                mean_monthly_higher_usd_per_lari_pct=np.mean([r["higher_usd_per_lari_pct"] for r in rows]))


def chart(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fixed, feedback = [[r for r in rows if r["case"] == "central" and r["policy"] == mode]
                       for mode in ("fixed", "endogenous")]
    with plt.rc_context({"font.family":"DejaVu Sans", "svg.fonttype":"none", "svg.hashsalt":"r3-feedback",
                         "axes.spines.top":False, "axes.spines.right":False}):
        fig, axes = plt.subplots(2, 2, figsize=(11.5, 7))
        for ax, (obs, alt, title, suffix) in zip(axes.flat, (
                ("observed_gel_per_usd", "no_purchases_gel_per_usd", "Month-end exchange rate", "GEL per USD"),
                ("observed_yoy_inflation_pct", "no_purchases_yoy_inflation_pct", "National all-items inflation", "% year on year"),
                ("observed_policy_rate_pct", "no_purchases_policy_rate_pct", "Month-end policy rate", "% per year"),
                (None, None, "Exchange-rate offset from monetary easing", "GEL per USD, endogenous minus fixed")), strict=True):
            if obs:
                for ds, field, color, style, label in ((fixed, obs, "#323b46", "-", "Observed"),
                      (fixed, alt, "#ba6328", "--", "Fixed policy rate"), (feedback, alt, "#08775e", "-.", "Endogenous policy rate")):
                    ax.plot(range(len(ds)), [r[field] for r in ds], color=color, ls=style, lw=2, label=label,
                            drawstyle="steps-post" if obs == "observed_policy_rate_pct" else "default")
            else:
                ax.axhline(0, color="#a0a7ad", lw=.7)
                ax.plot([a["no_purchases_gel_per_usd"]-b["no_purchases_gel_per_usd"] for a,b in
                         zip(feedback, fixed, strict=True)], color="#08775e", lw=2)
            ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
            ax.set_ylabel(suffix, fontsize=9)
            ax.set_xticks([0, 5, 11, 17, 20], ["Jan 25","Jun","Dec","Jun 26","Sep"])
            ax.grid(axis="y", alpha=.2)
        fig.subplots_adjust(left=.09, right=.975, top=.78, bottom=.09, wspace=.30, hspace=.47)
        fig.suptitle("Georgia without NBG FX purchases: the central calibration", x=.09, ha="left",
                     y=.975, fontsize=16, fontweight="bold")
        fig.legend(*axes[0,0].get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(.08,.934),
                   frameon=False, ncol=3)
        fig.text(.09,.84,"January 2025–September 2026  |  Common external shocks and minimum gross purchases removed.", fontsize=10)
        buf = io.StringIO()
        fig.savefig(buf, format="svg", metadata={"Date":None, "Creator":"GeorgianNationalBank research"})
        plt.close(fig)
    return "\n".join(line.rstrip() for line in buf.getvalue().splitlines()) + "\n"


def outputs(n=N):
    months, gdp, history, weights, _ = fx.load_inputs()
    prices, dates = headline(), episode_calendar(months)
    intervals = meeting_intervals(dates, n + len(months))
    ref = intervals[:n]
    b = demand_coefficient(ref)
    monthly, endpoints, impulses, calibration = [], [], [], []
    def run(s, k, domestic, fixed=False):
        return episode(months, gdp, history, weights, prices, dates, intervals, s, k, domestic, fixed, n)
    for s in SETTINGS:
        k = calibrate(ref, s, b)
        for fixed in (True, False):
            rows = run(s, k, b, fixed)
            monthly.extend(rows)
            endpoints.append(summary(rows, "reference"))
        unit = unit_fx(ref, s, k, b)
        tighten = project(np.zeros(n), ref, s, k, b, rate_shock=1)
        no_parity = project(np.zeros(n), ref, replace(s, parity=0), k, b, rate_shock=1)
        for h in range(61):
            impulses.append(dict(case=s.case.name, month_after_shock=h, unit_fx_gap_log_points=unit.quote[h],
                unit_fx_inflation_gap_pp=unit.inflation[h], unit_fx_rate_gap_pp=unit.rate[h],
                tightening_fx_gap_log_points=tighten.quote[h], tightening_inflation_gap_pp=tighten.inflation[h],
                tightening_rate_gap_pp=tighten.rate[h], tightening_no_parity_inflation_gap_pp=no_parity.inflation[h]))
        calibration.append(dict(case=s.case.name, fx_impact=s.case.impact, half_life_months=s.case.half_life,
            cpi_24m_decline_target_pp=s.target, cpi_24m_achieved_pp=unit.inflation[24], cpi_fx_loading=k,
            domestic_rate_loading=b, policy_slope=s.phi, quarterly_smoothing=s.smoothing,
            fx_price_stage_months=s.window, domestic_stage_months=18, parity_months=s.parity,
            tightening_24m_pp=tighten.inflation[24], tightening_trough_pp=np.min(tighten.inflation[:61]),
            tightening_trough_month=int(np.argmin(tighten.inflation[:61]))))
    s = SETTINGS[1]
    central_k = calibration[1]["cpi_fx_loading"]
    fast = replace(s, window=15)
    fast_k = calibrate(ref, fast, b)
    variations = [
        ("zero_purchase_impact", replace(s, case=replace(s.case, impact=0)), central_k, b),
        ("zero_pass_through", s, 0., b),
        ("zero_rate_to_fx", replace(s, parity=0), central_k, b),
        ("six_month_parity", replace(s, parity=6), central_k, b),
        ("two_year_parity", replace(s, parity=24), central_k, b),
        ("faster_price_adjustment_rematched", fast, fast_k, b),
        ("faster_price_adjustment_same_loading", fast, central_k, b),
        ("no_domestic_rate_channel", s, central_k, 0.),
        ("double_domestic_rate_loading", s, central_k, 2 * b),
        ("lower_policy_response", replace(s, phi=1.1), central_k, b),
        ("higher_policy_response", replace(s, phi=2.), central_k, b),
        ("diminishing_direct_impact", replace(s, case=replace(s.case, response="diminishing")), central_k, b),
        ("three_month_fx_half_life", replace(s, case=replace(s.case, half_life=3)), central_k, b),
        ("reversed_direct_fx_sign", replace(s, case=replace(s.case, impact=-s.case.impact)), central_k, b),
    ]
    sensitivities = []
    for label, modified, k, domestic in variations:
        rows = run(modified, k, domestic)
        sensitivities.append(dict(**summary(rows, label), cpi_fx_loading=k, domestic_rate_loading=domestic,
                                  policy_slope=modified.phi, parity_months=modified.parity,
                                  fx_price_stage_months=modified.window, direct_response=modified.case.response,
                                  fx_half_life_months=modified.case.half_life, fx_impact=modified.case.impact))
    return {"monthly.csv":csv_text(monthly), "endpoints.csv":csv_text(endpoints),
            "sensitivities.csv":csv_text(sensitivities), "impulses.csv":csv_text(impulses),
            "calibration.csv":csv_text(calibration), "central_paths.svg":chart(monthly)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpi-workbook", type=Path, help="Re-extract the frozen Geostat input")
    parser.add_argument("--check", action="store_true", help="Compare regenerated files byte for byte")
    args = parser.parse_args()
    def emit(path, content):
        if args.check:
            if path.read_bytes() != content.encode():
                raise SystemExit(f"Output differs: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode())
    if args.cpi_workbook:
        emit(CPI, extract_cpi(args.cpi_workbook))
    for name, content in outputs().items():
        emit(OUT / name, content)
    print(f"{'Verified' if args.check else 'Wrote'} policy feedback outputs")
