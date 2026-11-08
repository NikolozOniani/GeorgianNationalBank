"""Annual NBG accounts and independent reserve-model arithmetic. No causal estimation."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/paper'
RAW = ROOT / 'data/raw/paper'


def write(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)


def read(name):
    with (OUT / name).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))


def dollarization(r): return .6 - .1 * math.log1p(r)
def crisis_loss(r): return .1 * (1 + .5 * dollarization(r))
def crisis_loss_derivative(r): return -.005 / (1 + r)


def acquire():
    RAW.mkdir(parents=True, exist_ok=True)
    for source in json.loads((OUT / 'sources.json').read_text()):
        p = RAW / source['filename']
        if not p.exists():
            temp = p.with_suffix('.partial')
            temp.write_bytes(urllib.request.urlopen(source['url'], timeout=45).read())
            if hashlib.sha256(temp.read_bytes()).hexdigest() != source['sha256']:
                raise ValueError('Source vintage mismatch; partial retained: ' + str(temp))
            temp.replace(p)
        if hashlib.sha256(p.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError('Hash mismatch: ' + str(p))


def extract():
    from pypdf import PdfReader
    source = json.loads((OUT / 'sources.json').read_text())[0]
    path = RAW / source['filename']
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']: raise ValueError('Annual source changed')
    pdf = PdfReader(path)
    # PDF page numbers are one-based, distinct from printed annual-report pages.
    specs = [
        ('reserve_cash_interest',274,'Cash and cash equivalents'),
        ('reserve_security_interest',274,'comprehensive income (“FVOCI”)'),
        ('reserve_other_interest',274,'Other'),
        ('bank_interest_income',274,'Due from resident financial institutions'),
        ('policy_security_interest',274,'comprehensive income'),
        ('other_interest_income',274,'Investments measured at amortised cost'),
        ('cd_interest_expense',274,'Debt securities issued'),
        ('bank_interest_expense',274,'Due to resident financial institutions'),
        ('imf_interest_expense',274,'Due to the International Monetary Fund'),
        ('customer_interest_expense',274,'Due to customers'),
        ('lease_interest_expense',274,'Interest expense on lease liabilities'),
        ('total_interest_expense',274,'Total interest expense'),
        ('net_interest_income',274,'NET INTEREST INCOME'),
        ('fx_assets',276,'12,489,778'),
        ('gel_assets',276,'9,035,200'),
        ('total_assets',276,'TOTAL ASSETS'),
        ('bank_claims_gel',276,'Due from resident financial institutions'),
        ('fx_liabilities',277,'9,141,409'),
        ('gel_liabilities',277,'9,082,897'),
        ('currency_circulation',277,'Money issued in circulation'),
        ('total_liabilities',277,'TOTAL LIABILITIES'),
        ('total_equity',277,'TOTAL EQUITY'),
        ('bank_gel_correspondent',303,'Correspondent accounts in national currency'),
        ('bank_gel_overnight',303,'Overnight deposits in national currency'),
        ('bank_fx_required_reserves',303,'Obligatory reserves of banks in foreign currency'),
        ('bank_liabilities_total',303,'Total due to resident financial institutions'),
        ('mof_profit_payable',302,'Profit payable to the Ministry of Finance of Georgia'),
        ('currency_opening',304,'Balance as at 1 January'),
        ('banknotes_issued',304,'Banknotes issued into circulation'),
        ('coins_issued',304,'Coins issued into circulation'),
        ('banknotes_withdrawn',304,'Banknotes withdrawn from circulation'),
        ('coins_withdrawn',304,'Coins withdrawn from circulation')]
    rows=[]
    for key, page, label in specs:
        text=pdf.pages[page-1].extract_text()
        number=r'(\(?[\d,]+\)?)'
        if label[0].isdigit():
            pattern=r'^\s*('+re.escape(label)+r')\s+'+number+r'\s*$'
        else:
            pattern=r'^\s*'+re.escape(label)+r'\s+(?:\d{1,2}\s+)?'+number+r'\s+'+number+r'\s*$'
        matches=list(re.finditer(pattern,text,re.M))
        if not matches: raise ValueError(f'No source row {key}: {label}')
        pairs={m.groups() for m in matches}
        if len(pairs)!=1: raise ValueError('Ambiguous source row '+key+str(pairs))
        values=next(iter(pairs))
        for year, val in zip((2024,2023),values):
            value=int(val.replace(',','').replace('(','-').replace(')',''))
            rows.append(dict(series=key,year=year,value_gel_thousand=value,source_pdf_page=page,
                             source_printed_page=page-1,source_label=label,source_row=matches[0][0].strip(),
                             source_url=source['url'],source_sha256=source['sha256']))
    write('annual_accounts.csv',rows)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--acquire',action='store_true');parser.add_argument('--extract',action='store_true');a=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if a.acquire: acquire()
    if a.extract: extract()
    lockpath=OUT/'input_hashes.json'
    if lockpath.exists():
        for name,sha in json.loads(lockpath.read_text()).items():
            if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:raise ValueError('Reviewed input changed: '+name)
    d={(int(r['year']),r['series']):float(r['value_gel_thousand'])/1000 for r in read('annual_accounts.csv')}
    checks=[]; results=[]
    for y in (2023,2024):
        v=lambda key:d[y,key]
        ri=sum(v(k) for k in ['reserve_cash_interest','reserve_security_interest','reserve_other_interest'])
        pi=v('bank_interest_income')+v('policy_security_interest')
        pe=v('cd_interest_expense')+v('bank_interest_expense')
        income=ri+pi+v('other_interest_income')
        expenses=sum(v(k) for k in ['cd_interest_expense','bank_interest_expense','imf_interest_expense','customer_interest_expense','lease_interest_expense'])
        identities={'assets':v('fx_assets')+v('gel_assets')-v('total_assets'),
                    'liabilities':v('fx_liabilities')+v('gel_liabilities')-v('total_liabilities'),
                    'balance_sheet':v('total_assets')-v('total_liabilities')-v('total_equity'),
                    'interest_expenses':expenses-v('total_interest_expense'),
                    'net_interest':income+expenses-v('net_interest_income'),
                    'currency':sum(v(k) for k in ['currency_opening','banknotes_issued','coins_issued','banknotes_withdrawn','coins_withdrawn'])-v('currency_circulation')}
        checks += [dict(year=y,identity=k,residual_gel_million=x) for k,x in identities.items()]
        results.append(dict(year=y,reserve_interest_income_gel_m=ri,monetary_interest_income_gel_m=pi,
                            monetary_interest_expense_gel_m=-pe,monetary_net_interest_gel_m=pi+pe,
                            bank_net_interest_received_gel_m=v('bank_interest_income')+v('bank_interest_expense'),
                            total_net_interest_gel_m=v('net_interest_income'),
                            currency_plus_gel_bank_liabilities_gel_m=v('currency_circulation')+v('bank_gel_correspondent')+v('bank_gel_overnight'),
                            net_fx_accounting_position_gel_m=v('fx_assets')-v('fx_liabilities')))
    if any(abs(x['residual_gel_million'])>.0011 for x in checks):raise ValueError('Annual accounting failure')
    write('accounting_checks.csv',checks);write('annual_results.csv',results)
    scenarios=[]
    for start,end in ((.1,.2),(.2,.3),(.1,.3)):
        for probability in (.01,.05,.1):
            for carry in (.01,.02,.04):
                benefit=probability*(crisis_loss(start)-crisis_loss(end))
                cost=(1-probability)*carry*(end-start)
                scenarios.append(dict(start_reserves_gdp=start,end_reserves_gdp=end,crisis_probability=probability,
                                      assumed_normal_state_carry=carry,dollarization_change_pp=100*(dollarization(end)-dollarization(start)),
                                      expected_loss_reduction_pct_gdp=100*benefit,normal_state_weighted_carry_pct_gdp=100*cost,
                                      isolated_benefit_cost_ratio=benefit/cost,
                                      scope='Isolated dollarization-loss channel; not total reserve insurance benefit or replicated optimum'))
    write('reserve_channel_sensitivity.csv',scenarios)
    targets=[dict(paper_reference_ara_pct=base,target_ara_pct=target,required_stock_growth_pct=100*(target/base-1),
                  scope='Frozen ARA denominator; paper-vintage baseline, not current reserves') for base in (102,105) for target in (130,145,150)]
    write('reserve_target_arithmetic.csv',targets)
    panel=list(csv.DictReader((ROOT/'reports/nbg_policy_monthly_2020_2024.csv').open()))
    p={r['month']:r for r in panel}
    annual=list(csv.DictReader((ROOT/'reports/nbg_fx_annual_benchmarks.csv').open()))
    # Annual sign convention is documented in the prior benchmark: sales positive.
    bridges=[]
    for source in sorted(annual,key=lambda x:x['year']):
        year=int(source['year']);netpurchase=-float(source['total_net_sales_usd_m'])
        delta=float(p[f'{year}-12']['official_reserves_usd_m'])-float(p[f'{year-1}-12']['official_reserves_usd_m'])
        bridges.append(dict(year=year,reserve_stock_change_usd_m=delta,net_intervention_purchase_usd_m=netpurchase,
                            unexplained_composite_usd_m=delta-netpurchase,
                            limitation='Composite of government flows, valuation, investment income and other movements; not a loss or intervention estimate'))
    write('reserve_bridges.csv',bridges)
    digest={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [OUT/'annual_accounts.csv',ROOT/'reports/peer_review/credit_monthly_2020_2024.csv',ROOT/'reports/nbg_policy_monthly_2020_2024.csv',ROOT/'reports/nbg_fx_annual_benchmarks.csv']}
    (OUT/'input_hashes.json').write_text(json.dumps(digest,indent=2)+'\n')
    print(json.dumps({'annual_results':results,'checks':len(checks),'reserve_bridges':bridges,'isolated_case':scenarios[6]},indent=2))


if __name__=='__main__':main()
