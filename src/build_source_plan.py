"""Resolve the roadmap's public files from official NBG catalogue responses."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/episode_2026_11_09'
selection = {
    52: ('fx_auctions', ['D01']), 96: ('fx_market', ['D01', 'D02']),
    51: ('fx_daily_current', ['D03']), 67: ('fx_daily_history', ['D03']),
    99: ('neer_daily', ['D03']), 100: ('neer_monthly', ['D03']), 101: ('reer_monthly', ['D03']),
    104: ('bop_bpm6', ['D06', 'D08', 'D13']), 114: ('remittances', ['D06']),
    113: ('remittances_country', ['D06']),
    148: ('travel', ['D06']), 111: ('trade_country', ['D06']),
    110: ('reserve_assets', ['D08', 'D14']), 116: ('reserve_liquidity', ['D14']),
    46: ('refinancing', ['D09', 'D10']), 54: ('cd_auctions', ['D09', 'D10']),
    63: ('money_market', ['D09', 'D10']), 118: ('tibr', ['D10']),
    90: ('market_rates', ['D10']), 93: ('repo', ['D09', 'D10']),
    35: ('central_bank', ['D09', 'D12']), 42: ('depository_survey', ['D06', 'D13']),
    43: ('money_aggregates', ['D13']), 106: ('external_debt', ['D13', 'D14']),
    107: ('debt_schedule', ['D14']), 109: ('iip', ['D13', 'D14']),
    56: ('treasury_bills', ['D10', 'D16']), 88: ('treasury_notes', ['D10', 'D16']),
}
catalogue = {}
for path in RAW.glob('category_*.json'):
    for row in json.loads(path.read_text()):
        catalogue[row['id']] = row
plan = []
for identifier, (name, requirements) in selection.items():
    row = catalogue[identifier]
    plan.append(dict(id=name, url='https://nbg.gov.ge/fm/' + row['file'], format='xlsx',
                     requirements=requirements, definition=row['title'], catalogue_id=identifier,
                     table_code=row['code'], catalogue_update_date=row['updateDate'],
                     publication_date_scope='catalogue update, not observation-specific first release'))
extra = [
 ('fx_method', 'https://nbg.gov.ge/en/page/foreign-exchange-market', 'html', ['D03','D04']),
 ('fx_rules', 'https://nbg.gov.ge/en/page/foreign-exchange-auctions', 'html', ['D01','D04']),
 ('liquidity_method', 'https://nbg.gov.ge/en/page/liquidity-management', 'html', ['D09','D10']),
 ('purchases_2025', 'https://nbg.gov.ge/en/media/news/georgia-s-international-foreign-exchange-reserves-reach-a-historic-high-of-approximately-u', 'html', ['D01']),
 ('reserves_aug2026', 'https://nbg.gov.ge/en/media/news/as-of-august-2026-georgia-s-gross-international-reserves-reach-an-all-time-high-of-usd-8', 'html', ['D01','D08']),
 ('mof_debt', 'https://www.mof.ge/en/page/public-debt-statistics', 'html', ['D05','D16']),
 ('annual2025', 'https://nbg.gov.ge/fm/პუბლიკაციები/ანგარიშები/წლიური_ანგარიში/2025/annual-eng-2025.pdf?v=ghprb', 'pdf', ['D01','D08','D11','D12']),
 ('ara_landing', 'https://www.imf.org/external/datamapper/datasets/ARA', 'html', ['D13']),
 ('sofr', 'https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2020-01-01&endDate=2026-11-09', 'json', ['D07']),
 ('broad_dollar', 'https://www.federalreserve.gov/releases/h10/summary/jrxwtfb_nb.htm', 'html', ['D07']),
 ('vix', 'https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv', 'csv', ['D07']),
 ('ara_indicators', 'https://www.imf.org/external/datamapper/api/v1/indicators', 'json', ['D13']),
 ('ara_ratio', 'https://www.imf.org/external/datamapper/api/v1/Reserves_ARA/GEO', 'json', ['D13']),
 ('ara_money_ratio', 'https://www.imf.org/external/datamapper/api/v1/Reserves_M2/GEO', 'json', ['D13']),
 ('ara_debt_ratio', 'https://www.imf.org/external/datamapper/api/v1/Reserves_STD/GEO', 'json', ['D13']),
 ('ara_import_cover', 'https://www.imf.org/external/datamapper/api/v1/Reserves_M/GEO', 'json', ['D13']),
 ('bmatch_statement', 'https://nbg.gov.ge/en/media/news/statement-of-the-national-bank-of-geor-26', 'html', ['D04']),
 ('mof_external', 'https://www.mof.ge/en/ExternalPublicDebtStatistics', 'html', ['D05']),
 ('mof_reports', 'https://www.mof.ge/en/fl/mtavrobis_valis_koveltviuri_angarishi', 'html', ['D05']),
 ('operations_manual', 'https://nbg.gov.ge/en/page/monetary-policy-operations-manual', 'html', ['D04']),
]
extra += [(f'mof_external_{year}', f'https://www.mof.ge/en/ExternalPublicDebtStatistics/GetData?year={year}',
           'html_fragment', ['D05','D16']) for year in [2024,2025,2026]]
plan += [dict(id=i, url=u, format=f, requirements=r, definition='Primary source for ' + ', '.join(r)) for i,u,f,r in extra]
manifest=ROOT/'data/source_manifest.json'
if manifest.exists():
    locks={r['id']:r.get('sha256') or r.get('expected_sha256') for r in json.loads(manifest.read_text())}
    for row in plan:
        if locks.get(row['id']):row['sha256']=locks[row['id']]
        original=next((r for r in json.loads(manifest.read_text()) if r['id']==row['id']),{})
        if original.get('bytes'):row['bytes']=original['bytes']
(ROOT / 'data/source_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
print('Planned sources:', len(plan))
