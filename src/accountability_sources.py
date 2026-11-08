"""Refresh only supplemental official pages; preserve successful records on failure.

Does not download old survey/policy datasets. New HTML/PDF vintages are stored
by hash in ignored data/raw/accountability/. It never overwrites pinned inputs.
"""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/accountability'
SUPPLEMENTAL={
 'LAW':('Organic Law on NBG, Georgian final consolidation', 'https://manage.matsne.gov.ge/ka/document/view/101044',
        'Articles 3, 4, 20(1,3,5), 60, 61; latest listed amendment 15 October 2026. Current powers, not a reconstruction of every historical version.'),
 'CONSTITUTION':('Constitution of Georgia', 'https://www.constcourt.ge/ka/court/legislation/constitution-text',
                 'Article 68, especially paragraph 3; Article 69 audit scope expressly limited by Article 68.'),
 'DISCLOSURE2022':('NBG statement, 6 September 2022', 'https://nbg.gov.ge/en/media/news/statement-of-the-national-bank-of-geor-26',
                   'Paragraphs on 15-minute auction results, monthly BMatch statistics 25 days after month end, confidential trigger rules. Historical stated policy, not measured compliance.'),
 'COMMUNICATION':('NBG communication policy, currently served PDF',
   'https://nbg.gov.ge/fm/%E1%83%9E%E1%83%A3%E1%83%91%E1%83%9A%E1%83%98%E1%83%99%E1%83%90%E1%83%AA%E1%83%98%E1%83%94%E1%83%91%E1%83%98/%E1%83%9E%E1%83%9D%E1%83%9A%E1%83%98%E1%83%A2%E1%83%98%E1%83%99%E1%83%98%E1%83%A1_%E1%83%93%E1%83%9D%E1%83%99%E1%83%A3%E1%83%9B%E1%83%94%E1%83%9C%E1%83%A2%E1%83%94%E1%83%91%E1%83%98/nbg-communication-policy.pdf?v=enx19',
   'Section 2.2, printed p.4: BMatch publication in third week of following month; exact adoption/revision date not verified. Do not call this a verified 2025 revision.'),
 'TRANSMISSION':('NBG monetary transmission', 'https://nbg.gov.ge/en/page/monetary-policy-transmission-mechanism',
                  'Interest, exchange, credit and expectations channels; conditional mechanism, not an estimated Georgian household effect.'),
 'LIQUIDITY':('NBG liquidity management', 'https://nbg.gov.ge/en/page/liquidity-management',
              'Core principles; collateralized weekly refinancing, not an unconditional gift to banks.'),
 'OPERATIONS':('NBG open market operations', 'https://nbg.gov.ge/en/page/open-market-operations',
               'Refinancing, one-month operations, CDs, securities; instrument explanation is not quantities or costs.'),
 'REQUIREMENTS':('NBG minimum reserve requirements', 'https://nbg.gov.ge/en/page/minimum-reserve-requirements',
                 'Requirements by currency; lending/funding channel. No current reserve ratios quoted.'),
}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'reports/nbg_source_manifest.json').read_text())
    register={}
    old={'CPI':('group_cpi.xlsx','National monthly total index, 2020–2024 panel column cpi_monthly_pct'),
         'RATE':('policy_rate.xlsx','Dated decision/enforcement workbook; monthly rate in force'),
         'RESERVES':('reserves.xml','End-month USD million stock and components'),
         'TIBR':('tibr.xlsx','Overnight business-day rate; policy panel monthly arithmetic mean'),
         'ANNUAL2023':('annual2023.pdf','Printed p.60: auction net sales 166.8, BMatch net purchases 1445.5, total net purchases 1278.7, USD million'),
         'ANNUAL2024':('annual2024.pdf','Printed p.46 (PDF page 47): 382.1 + 52.65 = 434.75 USD million net sales; seven auctions in printed p.25 (PDF page 26)'),
         'IMF':('imf2025.pdf','Country Report 25/217, chapter pp.4–18, paragraphs 29–39; especially p.14 fig.19 and pp.15–17 caveats')}
    for key,(name,locator) in old.items():
        register[key]={**manifest[name],'locator':locator,'verification':'Reused from verified parent commit; no reacquisition'}
    usd=manifest['usd_month_end_api']['observations']['2024-12']
    register['USD']={**usd,'locator':'December 2024 official USD quote; other 59 response hashes in parent manifest'}
    pilot=json.loads((ROOT/'reports/pilot2017_validation.json').read_text())
    register['PILOT']={'source_url':'https://github.com/NikolozOniani/GeorgianNationalBank/releases/tag/GEOSTAT',
                      'sha256':pilot['survey_sha256'],'locator':'Actual asset 2017.zip; ../pilot2017_exposure.csv, ../pilot2017_validation.json and ../Pilot2017_Methods_and_Results.md; CPI source is CPI above',
                      'verification':'Existing validated outputs reused, no new microdata processing'}
    register['SCENARIO']={'source_url':'../../src/accountability_scenarios.py','locator':'Explicit hypothetical assumptions, not observed outcomes','sha256':None}
    raw=ROOT/'data/raw/accountability';raw.mkdir(parents=True,exist_ok=True)
    log=[]
    for key,(title,url,locator) in SUPPLEMENTAL.items():
        item=dict(title=title,source_url=url,locator=locator,accessed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'GeorgianNationalBankResearch/1.0'})
            with urllib.request.urlopen(req,timeout=35) as response:
                data=response.read();item.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type',''))
            if not data:raise ValueError('Empty response')
            sha=hashlib.sha256(data).hexdigest()
            suffix='.pdf' if data.startswith(b'%PDF') else '.html'
            path=raw/(key+'_'+sha+suffix)
            if not path.exists():path.write_bytes(data)
            item.update(sha256=sha,bytes=len(data),status='downloaded',raw_path=str(path.relative_to(ROOT)))
        except Exception as e:
            item.update(status='failed',error=str(e),sha256=None)
        register[key]=item;log.append({'source_id':key,**item})
        # Checkpoint after each source. A failed page cannot discard successful files.
        (OUT/'source_retrieval.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
    (OUT/'source_register.json').write_text(json.dumps(register,ensure_ascii=False,indent=2)+'\n')
    lines=['# Source register — accountability edition','',
           'Data parent: `43c00d543485d47069b5ddb9755e9363b733c512`. Supplemental primary-source check: 8 November 2026. Numerical analysis remains historical 2020–2024. Live HTML hashes identify bytes, not a legal certification or a stable future download. Raw supplemental snapshots are ignored; citations and retrieval records are committed.', '',
           'The Georgian final law was checked; older English translations are not used to establish current law. The communication PDF’s revision date is unverified. Publication schedules are statements, not an audit of actual release dates. Existing source-file hashes remain in the parent manifest.','']
    for key,item in register.items():
        lines += [f'## {key}', '',f'[{item.get("title",key)}]({item["source_url"]})', '',item['locator'],'',
                  'SHA-256: `'+str(item.get('sha256','see original manifest'))+'`.', '']
    (OUT/'sources.md').write_text('\n'.join(lines),encoding='utf-8')
    print({r['source_id']:r['status'] for r in log})


if __name__=='__main__':main()
