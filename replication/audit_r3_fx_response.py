"""Independent R3 step 2 audit. Run after the raw-workbook and output checks."""
import argparse
import csv
import json
import math
from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import date, datetime, timedelta
from itertools import islice
from pathlib import Path
from statistics import mean, median

import numpy as np
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/derived/r3_fx_response'
OUT = ROOT / 'reports/r3_fx_response'
PANEL = ROOT / 'reports/r3_reopen_2026_11_16/model_panel.csv'


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_number(actual, reported, label):
    if not math.isclose(actual, float(reported), abs_tol=1e-9, rel_tol=1e-9):
        raise ValueError(f'{label}: computed {actual}, reported {reported}')


def annual_quotes(path, expected):
    """Use only rows in each tab's named year. Some tabs also contain adjacent years."""
    book = load_workbook(path, read_only=True, data_only=True)
    quotes = {}
    try:
        for year in sorted({d.year for d in expected}):
            rows = iter(book[str(year)].values)
            header = list(islice(rows, 5))
            col = header[-1].index('USD')
            require(header[-2][col] == 1, f'USD units in {year}')
            for row in rows:
                if isinstance(row[0], datetime) and row[0].year == year:
                    day = row[0].date()
                    require(day not in quotes, f'Duplicate annual quote {day}')
                    quotes[day] = row[col]
    finally:
        book.close()
    require(quotes == expected, 'Annual tabs disagree with consolidated quote extract')
    return len(quotes)


def audit_auctions(prices, auctions):
    """Rebuild all admissible sets by scanning dates, independently of production code."""
    dates = sorted(date.fromisoformat(r['date']).toordinal() for r in auctions)
    require(len(dates) == len(set(dates)), 'Multiple cash-auction rows on one date')
    purchase = {date.fromisoformat(r['date']).toordinal(): float(r['purchases_usd']) / 1e6
                for r in auctions if float(r['purchases_usd']) > 0}
    quotes = {d.toordinal(): p for d, p in prices.items()}
    auction_set = set(dates)
    horizons = (1, 7, 28, 84)
    records = read(OUT / 'auction_pairs.csv')
    reported = {(date.fromisoformat(r['date']).toordinal(), int(r['h_days'])): r
                for r in records}
    expected = {(d, h) for d in purchase for h in horizons if d + h in quotes}
    require(reported.keys() == expected and len(records) == len(expected),
            'Purchase/horizon coverage or uniqueness')
    def change(start, end):
        return 100 * math.log(quotes[end] / quotes[start])

    def clear(anchor, h, include_end):
        stop = bisect_right(dates, anchor + h) if include_end else bisect_left(dates, anchor + h)
        return stop == bisect_right(dates, anchor)

    output = []
    for h in horizons:
        groups = defaultdict(list)
        for day in sorted(purchase):
            if (day, h) not in reported:
                continue
            row = reported[day, h]
            check_number(purchase[day], row['purchase_usdm'], 'Event quantity')
            event = change(day, day + h)
            check_number(event, row['observed_return'], 'Event return')
            for lag in (7, 28):
                check_number(change(day - lag, day), row[f'pre{lag}'], 'Event pretrend')
            eligible = []
            for c in range(day - 91, day - 13):
                if ((day - c) % 7 or c in auction_set or c + h >= day
                        or date.fromordinal(c).year != date.fromordinal(day).year):
                    continue
                distance = math.hypot(*(change(day - lag, day) - change(c - lag, c)
                                        for lag in (7, 28)))
                eligible.append((distance, -c))
            if not eligible:
                require(not row['control'], f'Spurious match {day}, {h}')
                continue
            distance, negative = min(eligible)
            control = -negative
            require(date.fromordinal(control).isoformat() == row['control'], 'Nonoptimal match')
            check_number(distance, row['distance_pp'], 'Match distance')
            for lag in (7, 28):
                check_number(change(control - lag, control), row[f'control_pre{lag}'], 'Control pretrend')
            difference = event - change(control, control + h)
            check_number(difference, row['difference_pp'], 'Matched return')
            groups['all'].append(difference)
            if clear(day, h, True) and clear(control, h, True):
                groups['exclude_through_endpoint'].append(difference)
            if clear(day, h, False) and clear(control, h, False):
                groups['exclude_before_endpoint'].append(difference)
            if control + h > day - 28:
                groups['original_match_overlaps_pretrend'].append(difference)
            disjoint = [pair for pair in eligible if -pair[1] + h <= day - 28]
            if disjoint:
                other = -min(disjoint)[1]
                groups['rematch_disjoint'].append(event - change(other, other + h))
        result = {'days': h}
        for label in ('all', 'exclude_through_endpoint', 'exclude_before_endpoint',
                      'original_match_overlaps_pretrend', 'rematch_disjoint'):
            values = groups[label]
            result[label] = {'pairs': len(values), 'mean_log_pp': round(mean(values), 6) if values else None}
        output.append(result)
    return output


def audit_event_summaries():
    pairs = read(OUT / 'auction_pairs.csv')
    fields = {'avg_pre7': 'pre7', 'avg_control_pre7': 'control_pre7',
              'avg_pre28': 'pre28', 'avg_control_pre28': 'control_pre28',
              'avg_observed': 'observed_return', 'avg_control': 'control_return',
              'avg_difference': 'difference_pp', 'avg_matching_distance': 'distance_pp'}
    table = read(OUT / 'auction_comparison.csv')
    expected = {(str(h), era, sample) for h in (1, 7, 28, 84)
                for era in ('all', 'pre_2020', '2020_onward') for sample in ('all_pairs', 'no_other_auction')}
    require(len(table) == len(expected) and
            {(r['h_days'], r['era'], r['sample']) for r in table} == expected, 'Auction summary coverage')
    for summary in table:
        era = summary['era']
        base = [r for r in pairs if r['h_days'] == summary['h_days'] and
                (era == 'all' or (r['date'] < '2020') == (era == 'pre_2020'))]
        matched = [r for r in base if r['control']]
        used = [r for r in matched if summary['sample'] == 'all_pairs'
                or r['other_auctions'] == r['control_other_auctions'] == '0']
        counts = (len(base), len(matched), len(used), len({r['control'] for r in used}))
        require(counts == tuple(int(summary[k]) for k in ('purchases', 'matched', 'used', 'unique_controls')),
                'Auction summary counts')
        values = {k: mean(float(r[field]) for r in used) for k, field in fields.items()} if used else {}
        if used:
            values['median_difference'] = median(float(r['difference_pp']) for r in used)
            values['placebo_28_to_7_difference'] = mean(float(r['pre28']) - float(r['pre7'])
                      - float(r['control_pre28']) + float(r['control_pre7']) for r in used)
        for k in [*fields, 'median_difference', 'placebo_28_to_7_difference']:
            if used:
                check_number(values[k], summary[k], k)
            else:
                require(summary[k] == '', f'Empty auction sample has a value for {k}')
    return len(table)


def settlement_comparison(auctions, months):
    """Test a next-weekday month assignment separately for each directional leg."""
    legs = [('purchases_usd', 'auction_buy_usdm'), ('sales_usd', 'auction_sell_usdm')]
    source = {r['month']: r for r in months}
    assigned = defaultdict(float)
    crossovers = []
    for r in auctions:
        trade = date.fromisoformat(r['date'])
        following = trade + timedelta(days=1)
        while following.weekday() > 4:
            following += timedelta(days=1)
        month = following.strftime('%Y-%m')
        if month not in source:
            continue
        for usd, usdm in legs:
            amount = float(r[usd]) / 1e6
            assigned[month, usdm] += amount
            if amount and month != r['date'][:7]:
                crossovers.append({'trade': r['date'], 'next_weekday': following.isoformat(),
                                   'leg': usd, 'amount_usdm': amount})
    for m, row in source.items():
        for _, leg in legs:
            check_number(assigned[m, leg], row[leg], f'Next-weekday comparison {m} {leg}')
    return {'directional_months_checked': 2 * len(months), 'cross_month_trades': crossovers}


def partial(x, controls):
    q, _ = np.linalg.qr(controls)
    return x - q @ (q.T @ x)


def audit_months(prices, auctions, panel):
    """Build origin and outcome rows on the full calendar before selecting periods."""
    months = read(DATA / 'monthly.csv')
    names = np.array([r['month'] for r in months])
    closes = {d.strftime('%Y-%m'): prices[d] for d in sorted(prices)}
    log_price = 100 * np.log([closes[m] for m in names])
    auction_net = defaultdict(float)
    for r in auctions:
        auction_net[r['date'][:7]] += (float(r['purchases_usd']) - float(r['sales_usd'])) / 1e6
    bank_net = np.array([float(r['auction_buy_usdm']) - float(r['auction_sell_usdm'])
                         + float(r['nonauction_net_usdm']) for r in months])
    np.testing.assert_allclose(bank_net, [float(r['net_usdm']) for r in months], rtol=0, atol=1e-9)
    revised_net = np.array([auction_net[r['month']] + float(r['nonauction_net_usdm']) for r in months])
    projections = read(OUT / 'monthly_projections.csv')
    specs = ('full', '2020_onward', '2020_global', 'full_dated_sensitivity')
    expected = {(s, h) for s in specs for h in (-1, 0, 1, 3, 6, 12, 18)}
    require(len(projections) == len(expected) and
            {(r['spec'], int(r['h_months'])) for r in projections} == expected, 'Projection coverage')
    deletions = []
    for row in projections:
        spec, h = row['spec'], int(row['h_months'])
        flow = (revised_net if spec == 'full_dated_sensitivity' else bank_net) / 100
        t = np.arange(2, len(flow) - max(0, h))
        if spec.startswith('2020'):
            t = t[names[t] >= '2020-01']
        if spec == '2020_global':
            t = np.array([i for i in t if panel[names[i]]['dollar_change_log_pct'] and panel[names[i]]['vix_mean']])
        lagged_return = log_price[t - 1] - log_price[t - 2]
        y = lagged_return if h == -1 else log_price[t + h] - log_price[t - 1]
        arms = [np.maximum(0, flow[t]), np.maximum(0, -flow[t])]
        common = [np.ones(len(t)), flow[t - 1]]
        if h >= 0:
            common.append(lagged_return)
        if spec == '2020_global':
            for key in ('dollar_change_log_pct', 'vix_mean'):
                common.append(np.array([float(panel[names[i]][key]) for i in t]))
        require((len(t), names[t[0]], names[t[-1]]) ==
                (int(row['n']), row['first_origin'], row['last_origin']), 'Monthly origins')
        for side, prefix, sign_count in [(0, 'buy', 'purchase_months'), (1, 'sale', 'sale_months')]:
            require(np.count_nonzero(arms[side]) == int(row[sign_count]), 'Treatment count')
            controls = np.column_stack([*common, arms[1-side]])
            x = partial(arms[side], controls)
            outcome = partial(y, controls)
            slope = x @ outcome / (x @ x)
            check_number(slope, row[prefix + '_logpct_per_100m'], 'Partial slope')
            error = outcome - slope * x
            influence = error * x / (x @ x)
            # Triangular HAC equals a sum of squares of zero-padded moving sums.
            window = max(h + 1, 1) + 1
            moving_sum = np.convolve(influence, np.ones(window))
            df = len(y) - controls.shape[1] - 1
            se = math.sqrt(moving_sum @ moving_sum / window * len(y) / df)
            check_number(se, row[prefix + '_hac_se'], 'Scalar HAC')
            if side == 0:
                rv = float(row['equal_partial_r2_to_zero'])
                check_number(rv / math.sqrt(1 - rv), abs(slope) * np.linalg.norm(x) / np.linalg.norm(error),
                             'Omitted-factor tipping point')
        if spec == '2020_global' and h == 18:
            years = [int(m[:4]) for m in names[t]]
            design = np.column_stack([*arms, *common])
            for year in sorted(set(years)):
                keep = np.array(years) != year
                subset = design[keep]
                require(np.linalg.matrix_rank(subset) == subset.shape[1], 'Rank after year deletion')
                coef = np.linalg.lstsq(subset, y[keep], rcond=None)[0][0]
                deletions.append({'omitted_origin_year': year, 'origins': int(keep.sum()),
                                  'buy_log_pp_per_usd100m': round(float(coef), 6)})
    episode = [float(r['net_purchases_usdm']) for m, r in panel.items() if '2025-01' <= m <= '2026-09']
    return {'specifications_times_horizons': len(projections), 'history_months': len(months),
            'episode_months': len(episode), 'historical_max_net_usdm': round(float(max(bank_net)), 6),
            'episode_above_historical_max': sum(v > float(max(bank_net)) for v in episode),
            'auction_settlement_sensitivity': settlement_comparison(auctions, months),
            'recent_global_h18_delete_origin_year': deletions}


def audit_kernels(panel):
    history = [row for m, row in sorted(panel.items()) if m < '2025-01']
    def series(key):
        return np.array([float(r[key]) if r[key] else np.nan for r in history])
    rates, y, q = (series(k) for k in ('policy_rate_pct', 'y', 'q_pct_gdp'))
    np.testing.assert_allclose(y, 100 * np.log(series('gel_per_usd')), rtol=0, atol=1e-8)
    np.testing.assert_allclose(q, 100 * series('net_purchases_usdm') / series('gdp_normalization_usdm'),
                               rtol=0, atol=1e-8)
    t = np.arange(3, len(y))
    controls = np.column_stack([np.ones(len(t)), rates[t], rates[t-1], series('dollar_change_log_pct')[t],
                                series('vix_mean')[t], q[t-1]])
    q0 = partial(q[t], controls)
    lagged_flows = np.column_stack([q[t-j] for j in range(4)])
    calibration = json.loads((ROOT / 'research/r3_reopen_calibration.json').read_text())
    primary, = [r for r in calibration if r['primary']]
    b = -np.array(primary['source_b_appreciation'])
    rho = primary['rho']
    settings = {'published': (rho, b), 'reversed': (rho, -b), 'zero': (rho, np.zeros(4)),
                'short_lived': (0.5, np.array([b[0], 0, 0, 0]))}
    records = read(OUT / 'kernel_diagnostics.csv')
    require(len(records) == len(settings) and {r['spec'] for r in records} == settings.keys(), 'Kernel coverage')
    for r in records:
        rho_i, coefficients = settings[r['spec']]
        shock = partial(y[t] - rho_i * y[t-1] - lagged_flows @ coefficients, controls)
        for number, key in [(len(t), 'n'), (rho_i, 'rho'), (coefficients[0], 'impact_logpct_per_1pct_gdp'),
                            (np.corrcoef(shock, q0)[0,1], 'partial_correlation'), (shock.std(ddof=1), 'residual_fx_sd'),
                            (q0.std(ddof=1), 'residual_q_sd')]:
            check_number(number, r[key], key)
    target = partial(y[t] - rho * y[t-1] - lagged_flows[:, 1:] @ b[1:], controls)
    for row in read(OUT / 'selection_sensitivity.csv'):
        shock = target - float(row['implied_impact_logpct_per_1pct_gdp']) * q0
        check_number(np.corrcoef(q0, shock)[0, 1], row['assumed_partial_correlation'], 'Correlation inverse')
    return {'preperiod_months_used': len(t),
            'correlation_at_zero_current_impact_fixed_published_lags': round(float(np.corrcoef(q0, target)[0, 1]), 6)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the new audit diagnostics')
    args = parser.parse_args()
    prices = {date.fromisoformat(r['date']): float(r['gel_usd']) for r in read(DATA / 'daily.csv')}
    manifest = json.loads((ROOT / 'data/source_manifest.json').read_text())
    path = ROOT / next(r['local_path'] for r in manifest if r['id'] == 'fx_daily_history')
    auctions = read(DATA / 'auctions.csv')
    panel = {r['month']: r for r in read(PANEL)}
    findings = {'audited_commit': 'fb62e1e0050ec76f6ec0fac5d2dcb53aeabdf5c2',
                'quotes_matching_annual_tabs': annual_quotes(path, prices),
                'auction_horizons': audit_auctions(prices, auctions), 'auction_summary_cells': audit_event_summaries(),
                'monthly': audit_months(prices, auctions, panel),
                'kernel': audit_kernels(panel)}
    dest = OUT / 'audit_diagnostics.json'
    if args.write:
        dest.write_text(json.dumps(findings, indent=2, allow_nan=False) + '\n')
    else:
        require(findings == json.loads(dest.read_text()), 'Audit diagnostics changed')
    print('R3 step 2 audit passed')


if __name__ == '__main__':
    main()
