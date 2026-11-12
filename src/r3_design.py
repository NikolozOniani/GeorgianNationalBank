"""Offline R3 eligibility audit and inverse sensitivity calculation. No estimator."""
import argparse
import csv
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/r3_2026_11_12/diagnostics.json'
PANEL = 'reports/acquisition_2026_11_09/monthly_policy_panel.csv'
FLOWS = 'reports/r1_2026_11_10/gross_flow_accounting_bounds.csv'
LEDGER = 'reports/r1_2026_11_10/episode_transaction_ledger.csv'


def read(name):
    with (ROOT / name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def required_impact(flows, retention, gap_pct):
    """log-rate basis points per USD 100m for a stipulated terminal gap."""
    exposure = 0.0
    for flow in flows:
        exposure = retention * exposure + float(flow) / 100
    return 10000 * math.log1p(gap_pct / 100) / exposure


def audit():
    flows = read(FLOWS)
    panel = {r['month']: r for r in read(PANEL)}
    periods = [f'{year}-{month:02}' for year, end in [(2025, 12), (2026, 9)]
               for month in range(1, end + 1)]
    if [r['period'] for r in flows] != periods:
        raise ValueError('Registered window or ordering changed')
    buys = []
    sales = []
    for row in flows:
        month = panel[row['period']]
        net = Decimal(row['net_market_purchases_usdm'])
        buy = Decimal(row['gross_market_purchases_lower_bound_usdm'])
        sale = Decimal(row['gross_market_sales_lower_bound_usdm'])
        if min(buy, sale) < 0 or buy - sale != net or abs(net - Decimal(month['net_market_purchases_usdm'])) > Decimal('0.00001'):
            raise ValueError('Flow reconciliation failed for ' + row['period'])
        buys.append(buy)
        sales.append(sale)
    ledger = read(LEDGER)
    opening = float(panel['2024-12']['official_usd_gel_end'])
    closing = float(panel[periods[-1]]['official_usd_gel_end'])
    return dict(
        input_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                      for name in (FLOWS, PANEL, LEDGER)},
        months=len(periods), net_usdm=str(sum(buys)-sum(sales)),
        purchases_floor_usdm=str(sum(buys)), sales_floor_usdm=str(sum(sales)),
        months_with_nonauction_gross_both=sum(bool(panel[t]['nonauction_gross_purchases_usdm']
                                                   and panel[t]['nonauction_gross_sales_usdm']) for t in periods),
        instrument_month_fields=len(ledger),
        fields_with_trade_date_and_execution_price=sum(bool(r['trade_date'] and r['execution_price']) for r in ledger),
        measured_opening_gel_per_usd=opening, measured_closing_gel_per_usd=closing,
        observed_quote_change_pct=100 * (closing/opening-1),
        stipulated_gap_pct=1,
        inverse_diagnostics=[dict(monthly_retention=rho,
                                  required_log_bp_per_usd100m=required_impact(buys, rho, 1))
                             for rho in (0, .5, 1)],
        identified_no_purchase_path=None, empirical_gap_interval=None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = json.dumps(audit(), indent=2, allow_nan=False) + '\n'
    if args.check:
        if REPORT.read_text() != output:
            raise SystemExit('R3 reproduction mismatch')
    else:
        REPORT.write_text(output)
