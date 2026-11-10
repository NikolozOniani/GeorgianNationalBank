"""R1 measured ledgers and explicit accounting residuals; no causal estimation.

Uses pinned November 9 observations and separately pinned November 10 documents.
All new outputs are staged before promotion. --check compares existing bytes.
"""
from __future__ import annotations
import argparse
import calendar
import csv
import datetime as dt
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re
import tempfile

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/derived/episode_2026_11_09'
DEST=ROOT/'reports/r1_2026_11_10'
START='2025-01'
END='2026-09'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dec(x):return D(str(x)) if x not in ('',None) else None
def csvrows(path):
    with path.open() as f:return list(csv.DictReader(f))
def read(name):return csvrows(DATA/(name+'.csv'))


def gross_bounds(net):
    """Accounting lower bounds; no finite upper bound without gross observations."""
    net=dec(net)
    return max(net,D(0)),max(-net,D(0))


class Build:
    def __init__(self,out):
        self.out=out;self.outputs=[];self.inputs={};self.checks=[];self.qualifications=[]
        self.sources={}
        for name in ['data/source_manifest.json','data/r1_source_manifest.json']:
            self.inputs[name]=sha(ROOT/name)
            for r in json.loads((ROOT/name).read_text()):
                if r['id'] in self.sources:raise ValueError('Duplicate source ID')
                self.sources[r['id']]=r
        catalogue=json.loads((DATA/'catalogue.json').read_text())
        for r in catalogue:
            if sha(ROOT/r['file'])!=r['sha256']:raise ValueError('Changed input '+r['file'])
            self.inputs[r['file']]=r['sha256']
        for ident in sorted({s for r in catalogue for s in r['source_ids']}):self.source(ident)

    def source(self,ident):
        r=self.sources[ident];p=ROOT/r['local_path']
        if r['status']!='acquired' or sha(p)!=r['sha256']:raise ValueError('Source mismatch '+ident)
        self.inputs[r['local_path']]=r['sha256']
        return p

    def check(self,name,passed,detail):
        self.checks.append(dict(check=name,passed=bool(passed),detail=detail))
        if not passed:raise ValueError(name+': '+str(detail))

    def save(self,name,rows,definition,units):
        assert rows,name
        p=self.out/(name+'.csv')
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
        self.outputs.append(dict(file=name+'.csv',rows=len(rows),sha256=sha(p),definition=definition,units=units))

    def transactions(self):
        allrows=read('intervention_monthly');self.monthly={r['month']:r for r in allrows}
        ledger=[];bounds=[]
        for r in allrows:
            m=r['month']
            if not START<=m<=END:continue
            for instrument,measure,key,location in [
                ('auction','gross_purchase','auction_purchases_usdm','USD_Sell-eng !D'+r['sell_row']),
                ('auction','gross_sale','auction_sales_usdm','USD_Buy-eng !C'+r['buy_row']),
                ('nonauction','net_purchase','nonauction_net_purchases_usdm','USD_Buy-eng !D'+r['buy_row']+'; sign reversed'),
                ('option','exercised_amount','options_exercised_usdm','USD_Sell-eng !C'+r['sell_row']),
                ('swap','reported_amount','nbg_swap_usdm','USD_Sell-eng !E'+r['sell_row'])]:
                ledger.append(dict(period=m,instrument=instrument,measure=measure,value_usdm=r[key],currency='USD',
                    observation_type='disclosed monthly aggregate',order_time=None,trade_date=None,settlement_date=None,
                    first_disclosure_date=None,execution_price=None,source_id='fx_market',source_locator=location,
                    status='observed net only; gross directions unknown' if instrument=='nonauction' else 'reported monthly field; not an execution event'))
            lowerp,lowers=gross_bounds(r['nonauction_net_purchases_usdm'])
            bounds.append(dict(period=m,net_market_purchases_usdm=r['net_market_purchases_usdm'],
                gross_market_purchases_lower_bound_usdm=lowerp+dec(r['auction_purchases_usdm']),
                gross_market_sales_lower_bound_usdm=lowers+dec(r['auction_sales_usdm']),
                gross_market_purchases_upper_bound_usdm=None,gross_market_sales_upper_bound_usdm=None,
                interpretation='P-S=N; P,S>=0. Lower bounds only; zero net does not imply zero gross.',source_id='fx_market'))
        self.check('episode_month_count',len(bounds)==21,len(bounds))
        self.save('episode_transaction_ledger',ledger,'Native monthly disclosures; no synthetic execution dates','USD million')
        self.save('gross_flow_accounting_bounds',bounds,'Accounting lower bounds, not observed gross transactions or causal bounds','USD million')
        summaries=[]
        for name,lo,hi in [('2025','2025-01','2025-12'),('2026_Jan_Sep','2026-01','2026-09'),('registered_episode',START,END)]:
            rows=[r for r in bounds if lo<=r['period']<=hi]
            summaries.append(dict(window=name,months=len(rows),net_purchases_usdm=sum(dec(r['net_market_purchases_usdm']) for r in rows),
                purchases_lower_bound_usdm=sum(r['gross_market_purchases_lower_bound_usdm'] for r in rows),
                sales_lower_bound_usdm=sum(r['gross_market_sales_lower_bound_usdm'] for r in rows)))
        self.save('episode_totals',summaries,'Monthly net totals and sums of monthly gross lower bounds; no finite upper bounds','USD million')
        events=read('fx_auction_events');checks=[]
        for m,r in self.monthly.items():
            if m>'2024-10':continue
            dated=sum((dec(x['purchases_usd'])-dec(x['sales_usd']))/D(1_000_000) for x in events if x['date'][:7]==m)
            reported=dec(r['auction_purchases_usdm'])-dec(r['auction_sales_usdm'])
            if dated!=reported:
                checks.append(dict(period=m,dated_event_net_usdm=dated,published_month_net_usdm=reported,
                    difference_usdm=dated-reported,status='consistent with T+1 crossing month; settlement not observed',
                    candidate_boundary_trade='2021-09-30' if m.startswith('2021') else '2022-08-31',
                    source_ids='fx_auctions;fx_market;monetary_manual_2021 paragraph 50'))
        self.check('auction_month_discrepancies_retained',len(checks)==4,checks)
        self.save('auction_timing_reconciliation',checks,'Original trade-date sums retained; no unobserved settlement-date reassignment','USD million')

    def matrices(self):
        import openpyxl
        self.position={};self.dcs={}
        for ident,sheet,rr in [('central_bank','Positions',range(4,17)),('depository_survey','DCS',range(4,39))]:
            w=openpyxl.load_workbook(self.source(ident),read_only=True,data_only=True);s=w[sheet];a=list(s.values);out=[]
            target=self.position if sheet=='Positions' else self.dcs
            for j,stamp in enumerate(a[2]):
                if not isinstance(stamp,dt.datetime) or not '2024-12'<=stamp.strftime('%Y-%m')<=END:continue
                day=stamp.date().isoformat();target[day]={}
                for n in rr:
                    value=a[n-1][j];assert isinstance(value,(int,float)),(ident,n,day)
                    target[day][n]=dec(value)
                    out.append(dict(date=day,series_row=n,label=str(a[n-1][0]).strip(),value_gelm=str(value),
                        source_id=ident,sheet=sheet,source_cell=f'{openpyxl.utils.get_column_letter(j+1)}{n}'))
            self.save('central_bank_positions' if sheet=='Positions' else 'depository_survey',out,
                'End-month positions include accruals/FX conversion; not transaction flows. DCS includes microbanks from Jan 2025.','GEL million')
            w.close()
        self.cbs={}
        for r in read('central_bank'):
            if '2024-12'<=r['date'][:7]<=END:self.cbs.setdefault(r['date'],{})[int(r['series_row'])]=dec(r['value'])
        def components(v):
            return dict(net_foreign_assets=v[4],claims_banks=v[19],net_claims_government=v[20],claims_other=v[28],
                other_nonbase_liabilities=-sum(v[k] for k in [40,41,49,50,51,52,53]),equity=-v[54],other_items_net=-v[60])
        levels=[];changes=[];prior=None;residuals=[]
        for day,v in sorted(self.cbs.items()):
            p=self.position[day];c=components(v)
            residual=v[34]-sum(c.values());residuals.append(abs(residual))
            self.check('position_bank_claims_'+day,abs(v[19]-p[9])<=D('.001'),str(v[19]-p[9]))
            self.check('position_instruments_'+day,abs(p[9]-sum(p[n] for n in [10,11,12,13]))<=D('.003'),str(p[9]-sum(p[n] for n in [10,11,12,13])))
            levels.append(dict(date=day,monetary_base_gelm=v[34],**{k+'_gelm':x for k,x in c.items()},
                currency_circulation_gelm=v[35],fx_required_reserves_gelm=v[37],gel_bank_correspondent_gelm=p[15],
                fx_correspondent_gelm=p[16],refinancing_gelm=p[10],one_month_operations_gelm=p[11],overnight_loans_gelm=p[12],
                government_deposits_gelm=v[26],identity_residual_gelm=residual,
                source_ids='central_bank: CBS and Positions',interpretation='Stocks; monetary base includes FX required reserves at current GEL exchange rates'))
            if prior:
                oldday,old=prior;oldc=components(old)
                changes.append(dict(month=day[:7],monetary_base_change_gelm=v[34]-old[34],
                    **{k+'_contribution_gelm':x-oldc[k] for k,x in c.items()},
                    identity_residual_gelm=(v[34]-old[34])-sum(c[k]-oldc[k] for k in c),
                    interpretation='Accounting stock changes, including valuation/accruals; not causal effects or purchase financing allocation'))
            prior=day,v
        self.check('monetary_base_identity',max(residuals)<=D('.006'),str(max(residuals)))
        for day,v in self.dcs.items():
            self.check('DCS_broad_money_'+day,abs(v[17]-v[18]-v[19]-v[25])<=D('.002'),str(v[17]-v[18]-v[19]-v[25]))
            self.check('DCS_NFA_'+day,abs(v[4]-v[5]+v[6])<=D('.002'),str(v[4]-v[5]+v[6]))
        self.save('liquidity_counterparts',levels,'Complete signed accounting counterparts of the monetary base, plus instrument breakdown','GEL million, end month')
        self.save('liquidity_changes',changes,'Changes of signed counterpart stocks; not transactions or attribution','GEL million per month')

    def reserve_bridge(self):
        stocks={r['date']:r for r in read('reserve_stocks_monthly')}
        self.stocks=stocks
        bop={r['date']:dec(r['value']) for r in read('bop_bpm6') if r['series_row']=='39'}
        rows=[]
        for period,transaction in sorted(bop.items()):
            if not re.fullmatch(r'202[56]Q[1-4]',period) or transaction is None:continue
            y=int(period[:4]);q=int(period[-1]);endmonth=q*3
            endpoint=dt.date(y,endmonth,calendar.monthrange(y,endmonth)[1]);start=dt.date(y,endmonth-2,1)-dt.timedelta(days=1)
            if endpoint.isoformat()[:7]>END:continue
            ms=[f'{y}-{m:02}' for m in range(endmonth-2,endmonth+1)]
            if not all(m in self.monthly for m in ms):raise ValueError(period)
            delta=dec(stocks[endpoint.isoformat()]['reserves_usdm'])-dec(stocks[start.isoformat()]['reserves_usdm'])
            net=sum(dec(self.monthly[m]['net_market_purchases_usdm']) for m in ms)
            rows.append(dict(period=period,reserve_change_usdm=delta,market_net_purchases_usdm=net,
                bop_reserve_transactions_usdm=transaction,other_transactions_residual_usdm=transaction-net,
                valuation_other_volume_revision_residual_usdm=delta-transaction,government_transactions_usdm=None,
                reserve_income_usdm=None,identified_fx_valuation_usdm=None,
                source_ids='reserve_assets;bop_bpm6;fx_market',status='Stock and transaction bridge; residual components unidentified'))
        self.save('reserve_flow_bridge',rows,'Native quarterly bridge; no monthly BOP interpolation','USD million')
        monthly=[]
        for m,r in self.monthly.items():
            if not START<=m<=END:continue
            y,mon=map(int,m.split('-'));date=dt.date(y,mon,calendar.monthrange(y,mon)[1]);before=dt.date(y,mon,1)-dt.timedelta(days=1)
            delta=dec(stocks[date.isoformat()]['reserves_usdm'])-dec(stocks[before.isoformat()]['reserves_usdm'])
            net=dec(r['net_market_purchases_usdm'])
            monthly.append(dict(month=m,reserve_change_usdm=delta,market_net_purchases_usdm=net,
                stock_change_less_purchases_usdm=delta-net,bop_reserve_transactions_usdm=None,
                government_transactions_usdm=None,identified_valuation_usdm=None,
                status='Composite residual only; monthly BOP/government/valuation decomposition unavailable',source_ids='reserve_assets;fx_market'))
        self.save('monthly_reserve_bridge',monthly,'Monthly stock change versus observed net market purchases; omitted components remain null','USD million')

    def annual(self):
        from pypdf import PdfReader
        reader=PdfReader(self.source('annual2025'));pages={n:reader.pages[n-1].extract_text() for n in [47,48,262,275]}
        facts=[]
        specs=[('government_fx_expenditure',2025,1600,'USD million',48,'1.6 billion','approximate; debt service plus other FX expenditure'),
            ('government_fx_loans_grants',2025,329.3,'USD million',48,'329.3 million','approximate; deposited at NBG'),
            ('reserve_management_revenue',2025,421.9,'GEL million',48,'421.9 million','narrative total; not identical to audited interest category'),
            ('gold_quantity',2025,229478,'troy ounces',262,'229,478','reported rounded physical quantity'),
            ('gold_quantity',2024,229478,'troy ounces',262,'229,478','reported rounded physical quantity'),
            ('gold_price',2025,4367.80,'USD per troy ounce',262,'4,367.80','reported year-end price'),
            ('gold_price',2024,2610.85,'USD per troy ounce',262,'2,610.85','reported year-end price'),
            ('gold_value',2025,1002.314,'USD million',262,'1,002,314','audited year-end holding value; original USD thousands'),
            ('gold_value',2024,599.133,'USD million',262,'599,133','audited year-end holding value; original USD thousands'),
            ('gold_unrealized_gain',2025,1019.691,'GEL million',262,'1,019,691','audited annual unrealized gain; not USD reserve-flow valuation'),
            ('policy_loans',2025,6167.078,'GEL million',262,'6,167,078','audited policy loans; excludes separately classified derivative assets'),
            ('policy_loans',2024,7003.577,'GEL million',262,'7,003,577','audited policy loans; excludes separately classified derivative assets')]
        for series,year,value,units,page,anchor,status in specs:
            self.check('PDF_'+series+'_'+str(year),anchor in pages[page],anchor)
            facts.append(dict(series=series,year=year,value=value,units=units,source_id='annual2025',pdf_page=page,anchor=anchor,status=status))
        self.save('annual_report_observations',facts,'Additional observations extracted from pinned annual report, approximate values marked','Mixed units as labeled')
        delta=dec(self.stocks['2025-12-31']['reserves_usdm'])-dec(self.stocks['2024-12-31']['reserves_usdm'])
        txn=next(dec(r['value']) for r in read('bop_bpm6') if r['date']=='2025' and r['series_row']=='39')
        net=sum(dec(r['net_market_purchases_usdm']) for m,r in self.monthly.items() if m.startswith('2025'))
        gold=D('1002.314')-D('599.133');price=D(229478)*(D('4367.80')-D('2610.85'))/D(1_000_000)
        self.check('gold_endpoint_price_bridge',abs(gold-price)<=D('.0011'),str(gold-price))
        overlap=[]
        for year,g in [(2024,D('599.133')),(2025,D('1002.314'))]:
            statistical=dec(self.stocks[f'{year}-12-31']['gold_usdm']);gap=statistical-g
            overlap.append(dict(year=year,audited_gold_usdm=g,statistical_gold_usdm=statistical,difference_usdm=gap,
                reconciled_within_rounding=abs(gap)<=D('.001'),source_ids='annual2025 p262;reserve_assets',
                interpretation='Keep source valuations separate; unexplained difference not allocated to transactions'))
            if abs(gap)>D('.001'):
                self.qualifications.append(dict(id='gold_source_overlap_'+str(year),difference_usdm=str(gap),status='unresolved valuation convention/vintage difference'))
        self.save('gold_source_concordance',overlap,'Audited and statistical gold valuations retained separately','USD million')
        statistical_gold=dec(self.stocks['2025-12-31']['gold_usdm'])-dec(self.stocks['2024-12-31']['gold_usdm'])
        rows=[('reserve_change',delta,'measured stock difference'),('market_net_purchases',net,'observed net market flow'),
            ('bop_transactions',txn,'observed BOP reserve asset transactions'),('government_inflows_approx',D('329.3'),'approximate narrative government loans/grants'),
            ('government_outflows_approx',D('-1600'),'approximate narrative government debt service and other FX expenditure'),
            ('remaining_transaction_residual_approx',txn-net-D('329.3')+D('1600'),'about USD 46 million; precision limited by approximate government outflows; income/other/revisions unresolved'),
            ('all_nontransaction_residual',delta-txn,'valuation/other volume/revision composite'),
            ('gold_holding_value_change',gold,'endpoint value change with unchanged reported gold quantity; not proof of no intrayear trading'),
            ('gold_constant_quantity_price_component',price,'endpoint quantity times USD price difference; mechanical price bridge'),
            ('statistical_gold_value_change',statistical_gold,'statistical reserve component change; 2024 audited comparison differs'),
            ('nontransaction_residual_less_audited_gold_change',delta-txn-gold,'cross-definition diagnostic only; do not call this a reconciled valuation component'),
            ('nontransaction_residual_less_statistical_gold_change',delta-txn-statistical_gold,'same-statistical-series conditional remainder; full gold valuation still requires transactions')]
        self.save('annual_2025_refined_bridge',[dict(component=k,value_usdm=v,interpretation=s,source_ids='annual2025 pp47-48,262;reserve_assets;bop_bpm6;fx_market') for k,v,s in rows],
            'Precise stock/transaction bridge plus separately approximate government and gold endpoint components; not a fully reconciled flow account','USD million')
        financing=[]
        for year,vals in [(2025,['59.384','-4.245','255.195','-255.756','4.772','59.350']),
                          (2024,['59.225','-4.638','255.034','-255.361','5.124','59.384'])]:
            numbers=[D(x) for x in vals]
            for value in numbers:
                anchor=f'{int(abs(value)*1000):,}'
                self.check(f'CD_PDF_{year}_{anchor}',anchor in pages[275],anchor)
            residual=sum(numbers[:-1])-numbers[-1]
            self.check('CD_stock_cash_accrual_'+str(year),residual==0,str(residual))
            financing.append(dict(year=year,opening_gelm=numbers[0],interest_paid_gelm=numbers[1],cash_issuance_gelm=numbers[2],
                cash_redemption_gelm=numbers[3],interest_accrued_gelm=numbers[4],closing_gelm=numbers[5],residual_gelm=residual,
                source_id='annual2025',pdf_page=275,interpretation='Audited NBG debt securities; not government Treasury securities or marginal reserve financing'))
        self.save('cd_financing_reconciliation',financing,'Audited stock/cash/accrual bridge; no marginal reserve cost attribution','GEL million')

    def treasury(self):
        import openpyxl
        rows=[]
        for ident in ['treasury_bills','treasury_notes']:
            w=openpyxl.load_workbook(self.source(ident),read_only=True,data_only=True);s=w.worksheets[0]
            for i,r in enumerate(s.values,1):
                if len(r)<13 or not isinstance(r[2],dt.datetime) or not START<=r[2].strftime('%Y-%m')<=END:continue
                notes=ident=='treasury_notes'
                rows.append(dict(instrument='treasury_note' if notes else 'treasury_bill',auction_number=r[0],isin=r[1],
                    value_date=r[2].date().isoformat(),auction_trade_date=None,maturity_date=r[4].date().isoformat(),
                    maturity_days=r[3],offered_gel=r[7],demand_gel=r[8],primary_purchase_gel=r[9],
                    noncompetitive_gel=r[10] if notes else None,switch_issuance_gel=r[11] if notes else None,
                    total_nominal_gel=r[12] if notes else None,weighted_rate_pct=r[15] if notes else r[11],
                    rate_definition='weighted average yield' if notes else 'weighted average discount rate',
                    reported_settlement_price_gel=r[17] if notes else None,
                    source_id=ident,sheet=s.title,source_row=i,
                    status='Government financing; not NBG sterilization. Value Date retained; blank supplementary amounts not assumed zero.'))
            w.close()
        self.check('treasury_rate_units_and_order',all(0<=r['weighted_rate_pct']<=100 and r['value_date']<r['maturity_date'] for r in rows),'Percent, not decimal fractions; value precedes maturity')
        self.check('treasury_native_record_count',len(rows)==126,len(rows))
        self.save('treasury_operations',rows,'Native value dates; current note sheet includes switch issuance; not net government cash flow','GEL amounts; annual percent discount rates (bills) or yields (notes), labeled separately')

    def information(self):
        from pypdf import PdfReader
        for ident in ['bmatch_statement','fx_rules','fx_method','purchases_2025','reserves_aug2026']:self.source(ident)
        manual=PdfReader(self.source('monetary_manual_2021')).pages[12].extract_text()
        instruments=PdfReader(self.source('instruments_2023')).pages[13].extract_text()
        news=self.source('purchase_disclosure_aug2025').read_text()
        self.check('historical_rule_threshold_description','predetermined mark' in manual,'Paragraph 52; numerical mark absent')
        self.check('historical_auction_settlement','next business day' in manual,'Paragraph 50')
        self.check('historical_instrument_window','15:45' in instruments and '16:00' in instruments,'2023 PDF p14')
        self.check('dated_purchase_disclosure','101.7' in news and '416.9' in news and '25 August' in news,'2025-08-25 article')
        timeline=[
            ('2020','','rule introduction','monetary_manual_2021','PDF p13 paragraph 52','Historical BMatch rule triggered by exchange-rate movement; threshold and episode version not supplied','year only, no invented day'),
            ('2023','','operating description','instruments_2023','PDF p14','Auctions mainly 15:45–16:00; BMatch during business hours; T+1 stated for auction settlement','historical operational guidance, not observed execution times'),
            ('2025-03','2025-12','annual narrative reference period','annual2025','PDF p47','Annual report places rule-based BMatch accumulation from March through year end','actual first execution date and report first publication unknown'),
            ('2025-01','2025-07','period disclosed on 2025-08-25','purchase_disclosure_aug2025','dated article, monthly bullet list','Jan–Feb no net purchases; March onward positive monthly net purchases','observed article date, not proven first disclosure of each earlier month'),
            ('2026-02-06','','disclosure','purchases_2025','dated article','Reports full-year 2025 net purchases; announces January release on February 25','announcement of future release is not observed execution or proof release occurred'),
            ('2026-09-07','','disclosure','reserves_aug2026','dated article','August reserve release includes January–July intervention benchmark','intervention and reserve reference months differ'),
            ('2026-11-09','','retrieval vintage','fx_market','manifest timestamp','Snapshot contains monthly observations through September 2026','retrieval date is not historical information availability')]
        self.save('information_timeline',[dict(reference_start=a,reference_end=b,event_type=c,source_id=d,source_locator=e,finding=f,limitation=g) for a,b,c,d,e,f,g in timeline],
            'Dated disclosures, reference periods and historical operational rules; actual order/trade/settlement remains unknown','Dates or explicitly year/month-only intervals')
        rule=[
            ('BMatch trigger','monetary_manual_2021','p13 paragraph 52','Exchange-rate fluctuation beyond a predetermined mark','Numerical threshold, lookback, order size, caps, overrides and 2025–2026 version unavailable'),
            ('BMatch matching','bmatch_statement','2022 statement','Orders matched by available price; this describes counterparty matching','Does not identify the timing/size assignment rule or exogenous variation'),
            ('Options trigger','monetary_manual_2021','p13 paragraph 51','Separate option exercise rule refers to previous 20-day average','Do not transfer this rule to BMatch; instrument activity requires its own observations'),
            ('Auction notice and settlement','monetary_manual_2021','p13 paragraph 50','Prior notice to banks and next-business-day settlement','Does not establish actual historical settlement dates or holidays'),
            ('Government FX route','fx_rules','Foreign exchange auctions page','Government accounts at NBG can bypass market','Does not reveal transaction-level government conversions'),
            ('Official FX fixing','fx_method','methodology page','Weighted trading window ending 16:30; next-day valid rate','Not an intraday pre-intervention quote; exact trade data not retrieved'),
            ('CBS reporting','central_bank','Notes rows4,7','Monthly publication schedule and end-month accrual/FX conversion','General schedule is not a historical release timestamp'),
            ('DCS definition break','depository_survey','DCS rows42–43','Institutional sector update September 2022; microbanks from January 2025','Do not interpret a composition change as economic flow')]
        self.save('rule_and_definition_register',[dict(item=a,source_id=b,locator=c,observed_description=d,remaining_gap=e) for a,b,c,d,e in rule],
            'Source-backed methodological descriptions, not confirmed complete episode rule calibration','Text')

    def discrepancies(self):
        old=json.loads((ROOT/'reports/acquisition_2026_11_09/validation.json').read_text())
        self.inputs['reports/acquisition_2026_11_09/validation.json']=sha(ROOT/'reports/acquisition_2026_11_09/validation.json')
        rows=[]
        for r in old['checks']:
            if r['passed']:continue
            rows.append(dict(id=r['check'],status='qualified; not repaired',details=r['detail'],action=r['qualification']))
        rows.extend([
            dict(id='2023_annual_net',status='unresolved definition/revision difference',details='Current monthly net 1279.25 versus annual 1278.7 USDm; nonauction 1446.0 versus 1445.5; auction sales 166.75 versus 166.8',action='Preserve both; no forced proportional allocation'),
            dict(id='fx_total_2026_02',status='quarantined aggregate',details='Bank-sell total minus reported components = -522.66170405 USDm',action='Exclude this aggregate from validated turnover; retain other observations and source components'),
            dict(id='gross_BMatch',status='unavailable at required granularity',details='Monthly net known; gross daily sides, prices and timestamps not retrieved',action='Use accounting lower bounds only; request existing anonymized execution extract'),
            dict(id='gold_valuation_scope',status='endpoint price bridge only',details='Equal year-end gold quantity; USD value change and GEL unrealized gain observed',action='Do not equate endpoint USD change to fully identified BOP gold valuation without gold transactions'),
            dict(id='government_2025',status='partial approximate disclosure',details='Approximate annual inflow/outflow newly extracted; no monthly conversion ledger',action='Report approximate residual, not measured investment income'),
            dict(id='first_disclosure',status='incomplete',details='Dated August 2025 and February/September 2026 releases do not identify every first release',action='No synthetic historical information dates')])
        rows.extend(self.qualifications)
        (self.out/'discrepancy_register.json').write_text(json.dumps(rows,indent=2)+'\n')

    def finish(self):
        self.discrepancies()
        for name,data in [('catalogue.json',self.outputs),('inputs.lock.json',self.inputs),('validation.json',dict(
            baseline_commit='92f05d27ab980c2f471e9ca24ab64c2884283860',checks=self.checks,all_computational_checks_passed=True,
            G1_status='PARTIAL; gross execution and full stock-flow decomposition not recovered',
            causal_estimation_performed=False,registered_window=[START,END],source_qualifications_remain=True,new_source_qualifications=self.qualifications))]:
            (self.out/name).write_text(json.dumps(data,indent=2,default=str,ensure_ascii=False)+'\n')
        used=[r for r in self.sources.values() if r['local_path'] in self.inputs]
        (self.out/'sources.json').write_text(json.dumps(used,indent=2,ensure_ascii=False)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='r1-build-') as folder:
        out=Path(folder);b=Build(out)
        b.transactions();b.matrices();b.reserve_bridge();b.annual();b.treasury();b.information();b.finish()
        if a.check:
            for f in out.iterdir():
                if not (DEST/f.name).exists() or (DEST/f.name).read_bytes()!=f.read_bytes():raise ValueError('Output mismatch '+f.name)
        else:
            DEST.mkdir(parents=True,exist_ok=True)
            for f in out.iterdir():
                temp=(DEST/f.name).with_suffix(f.suffix+'.partial');temp.write_bytes(f.read_bytes());temp.replace(DEST/f.name)
        print(json.dumps(dict(outputs=len(b.outputs),checks=len(b.checks),G1='partial; request-dependent gaps retained')))


if __name__=='__main__':main()
