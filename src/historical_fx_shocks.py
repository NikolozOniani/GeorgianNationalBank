"""Reproduce the historical screen and the 2008 monthly stock ledger from locked NBG vintages."""
import argparse
import calendar
import csv
import hashlib
import io
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/historical_fx_shocks"


def table(key, sheet):
    manifest = json.loads((ROOT / "data/source_manifest.json").read_text())
    record = next(r for r in manifest if r["id"] == key)
    path = ROOT / record["local_path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
        raise ValueError(f"Source lock failed for {key}")
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        return list(book[sheet].values)
    finally:
        book.close()


def end(year, month):
    return date(year, month, calendar.monthrange(year, month)[1])


def observations(rows, col, scale=1):
    return {r[0].date(): r[col] / scale for r in rows
            if isinstance(r[0], datetime) and isinstance(r[col], (int, float))}


def screen():
    reserves = observations(table("reserve_assets", "GIR (eng) "), 1, 1000)
    deposits = observations(table("money_aggregates", "Monetary Ratios-eng"), 9)
    raw = table("fx_daily_history", "2001-2025")
    quotes = observations(raw, raw[5].index("USD"))
    bop = table("bop_bpm6", "BOP–BPM6")
    cols = {v: i for i, v in enumerate(bop[2]) if re.fullmatch(r"\d{4}Q[1-4]", str(v))}
    debt = table("external_debt", "ED-GEO-Tb1")
    # Bind each cell address to its sector, maturity and instrument header.
    for number, label in [(32, "Deposit-Taking Corporations, except the Central Bank"),
                          (33, "Short-term"), (36, "Loans"), (39, "Long-term"), (42, "Loans")]:
        if debt[number-1][0].strip() != label:
            raise ValueError(f"Unexpected external debt label at row {number}")
    stocks = {v.date(): debt[35][i] + debt[41][i] for i, v in enumerate(debt[2])
              if isinstance(v, datetime) and 2007 <= v.year <= 2024}
    indicators = ["exports", "bank_loans", "fx_deposits"]
    rows = []
    for year in range(2008, 2025):
        for q in range(1, 5):
            label = f"{year}Q{q}"
            close = end(year, 3*q)
            opening = date(year, 3*q-2, 1) - timedelta(days=1)
            i = cols[label]
            previous = bop[7][cols[f"{year-1}Q{q}"]]
            current = bop[7][i]
            bank = bop[714][i]
            old_deposit = deposits[opening] / quotes[opening]
            new_deposit = deposits[close] / quotes[close]
            delta = reserves[close] - reserves[opening]
            trans = bop[836][i]
            row = dict(quarter=label, exports_usdm=current, prior_year_exports_usdm=previous,
                       bank_net_loan_incurrence_usdm=bank, opening_bank_external_loans_usdm=stocks[opening],
                       opening_fx_deposits_usdm=old_deposit, closing_fx_deposits_usdm=new_deposit,
                       reserves_change_usdm=delta, reserve_transactions_usdm=trans,
                       other_stock_changes_usdm=delta-trans)
            for name, gap, base in zip(indicators, (previous-current, -bank, old_deposit-new_deposit),
                                       (previous, stocks[opening], old_deposit)):
                if base <= 0:
                    raise ValueError(f"Invalid exposure in {label}: {name}")
                row[name+"_pressure_pct"] = 100*gap/base
            rows.append(row)
    for name in indicators:
        key = name+"_pressure_pct"
        scores = sorted((r[key] for r in rows), reverse=True)
        for row in rows:
            row[name+"_rank"] = scores.index(row[key])+1
    for row in rows:
        row["flagged_channels"] = "|".join(k for k in indicators if row[k+"_rank"] <= 5 and row[k+"_pressure_pct"] > 0)
    mid = {k: median(r[k+"_rank"] for r in rows) for k in indicators}
    control = min(rows, key=lambda r: sum(abs(r[k+"_rank"]-mid[k]) for k in indicators))
    windows = []
    current_window = []
    for row in rows + [{"flagged_channels": ""}]:
        if row["flagged_channels"]:
            current_window.append(row)
        elif current_window:
            windows.append(dict(start=current_window[0]["quarter"], finish=current_window[-1]["quarter"],
                                kind="flagged", reason="; ".join(r["quarter"]+" "+r["flagged_channels"] for r in current_window)))
            current_window = []
    for first, last in [("2008Q1","2008Q4"),("2014Q1","2015Q4"),("2020Q1","2020Q4"),("2022Q1","2022Q4")]:
        windows.append(dict(start=first, finish=last, kind="named_review", reason="pre-specified"))
    windows.append(dict(start=control["quarter"], finish=control["quarter"], kind="comparison", reason="closest to median ranks"))
    monthly = []
    for month in range(1,13):
        d = end(2008,month)
        prev = d.replace(day=1)-timedelta(days=1)
        monthly.append(dict(month=d.strftime("%Y-%m"), reserves_usdm=reserves[d],
                            reserves_change_usdm=reserves[d]-reserves[prev],gel_per_usd=quotes[d],
                            fx_deposits_gelm=deposits[d],fx_deposits_usdm=deposits[d]/quotes[d],
                            fx_deposits_change_usdm=deposits[d]/quotes[d]-deposits[prev]/quotes[prev]))
    for i in range(4):
        if abs(sum(r["reserves_change_usdm"] for r in monthly[3*i:3*i+3])-rows[i]["reserves_change_usdm"]) > 1e-7:
            raise ValueError("Monthly reserve movements do not reconcile to the quarter")
    return {"screen.csv": rows, "windows.csv": windows, "georgia_2008_monthly.csv": monthly}


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--check", action="store_true")
    check = args.parse_args().check
    for name, rows in screen().items():
        f = io.StringIO()
        writer = csv.DictWriter(f, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v,float) else v) for k,v in row.items()})
        data = f.getvalue().encode()
        if check:
            if data != (OUT/name).read_bytes():
                raise ValueError(f"Reproduction failed for {name}")
        else:
            (OUT/name).write_bytes(data)


if __name__ == "__main__":
    main()
