"""Generate the review packet's source register and numerical claim ledger."""
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/peer_review'


def read(name):
    with (OUT / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    sources = json.loads((OUT / 'sources.json').read_text())
    old = json.loads((ROOT / 'reports/nbg_source_manifest.json').read_text())
    register = ['# Exact sources and interpretive locators', '',
                'Reviewed vintage acquired 8 November 2026. Full source bytes are kept outside git; hashes below pin the reviewed files. Current provider URLs can change in place. The committed observations remain reproducible offline.', '']
    for s in sources:
        register += ['## ' + s['id'], '',
                     '[' + s['title'] + '](' + quote(s['url'], safe=':/?=%&') + ')', '',
                     '- File: `' + s['filename'] + '`; bytes: ' + str(s['bytes']) + '.',
                     '- SHA-256: `' + s['sha256'] + '`.']
        if s.get('catalog_update_date'):
            register += ['- Catalog update: ' + s['catalog_update_date'] + '; [official catalog](' + s['catalog_url'] + '). This is not a reconstructed historical publication date.']
        if s['id'] == 'L3.14':
            register += ['- Acquired but not used in the core extraction. Household consumer-loan stocks and rates; distinct from new-loan flow pricing.']
        if s['id'] == 'FSR2024':
            register += ['- Household analysis pp.22–23; broader bank portfolio p.50. The 42% household adjustable-rate share is not a GEL-specific reset distribution. The 43% GEL and 52% FX shares refer to the broader banking portfolio.',
                         '- [Official announcement, 25 September 2024](https://nbg.gov.ge/en/media/news/financial-stability-and-monetary-policy-committees-decisi-2). The report is not a December 2024 contract census.']
        if s['id'] == 'FSR2023':
            register += ['- Page 58: broader banking portfolio currency shares, not household-specific scaling weights.']
        register += ['']
    for id, key in [('RATE', 'policy_rate.xlsx'), ('IMF2025', 'imf2025.pdf')]:
        s = old[key]
        register += ['## ' + id, '', '[Previously verified official source](' + s['source_url'] + ')', '',
                     '- Source-file SHA-256: `' + s['sha256'] + '`.',
                     '- Reused from `reports/nbg_source_manifest.json`; not downloaded again for this chapter.', '']
    register += ['RATE is processed in `reports/nbg_policy_decisions_2008_onward.csv`; use effective dates rather than announcement dates. Its processed-file hash is in `analysis_inputs.lock.json`.', '',
                 'IMF2025 is Country Report 25/217, Georgia: Selected Issues. Paragraph 29 and its surrounding qualifications supply model-dependent counterevidence for the wider investigation; no IMF estimate is added to or subtracted from this paper’s loan calculations.', '',
                 '## PILOT2017', '',
                 '[Prior pilot methods and results](../Pilot2017_Methods_and_Results.md), `../pilot2017_validation.json`, and `../pilot2017_exposure.csv`. These files are preserved from the starting research commit. The pilot is partial category coverage and is not linked to borrower contracts.', '',
                 '## Cell-level audit', '',
                 '`credit_observations.csv` identifies every numeric cell and its corresponding date cell. `series_dictionary.csv` contains the header checks, populations and units. `claim_ledger.csv` provides precise source cells for the headline endpoint comparisons and explicit assumptions for calculated amounts.', '']
    (OUT / 'Sources.md').write_text('\n'.join(register), encoding='utf-8')
    by_source = {s['id']: s for s in sources}
    obs = {(r['month'], r['series']): r for r in read('credit_observations.csv')}
    dictionary = {r['series']: r for r in read('series_dictionary.csv')}
    ledger = []

    def add(**kw):
        fields = ['claim_id', 'claim', 'evidence_class', 'value', 'units', 'period',
                  'source_url', 'source_sha256', 'source_locator', 'calculation',
                  'uncertainty', 'limitation', 'counterargument', 'defensible_response',
                  'action_if_verification_fails']
        ledger.append({k: kw.get(k, '') for k in fields})

    for i, row in enumerate(read('table1_observed.csv'), 1):
        key = row['series']
        for month, field in [('2020-12', 'dec2020'), ('2022-12', 'dec2022'), ('2024-12', 'dec2024')]:
            o = obs[month, key]; s = by_source[o['source_id']]
            add(claim_id=f'A{i:02}-{month}', claim=key, evidence_class='A: documented official aggregate',
                value=row[field], units=o['unit'], period=month, source_url=s['url'], source_sha256=s['sha256'],
                source_locator=f"{s['filename']} / {o['sheet']}!{o['cell']}; date {o['date_cell']}",
                calculation='Direct source value; no imputation', uncertainty='Current vintage; source precision and revisions; no sampling CI computed',
                limitation=dictionary[key]['population'] + '; stock and flow measures differ',
                counterargument='Portfolio composition changes; aggregate average is not same-borrower repricing',
                defensible_response='Only the reported portfolio level is claimed; no policy attribution',
                action_if_verification_fails='Correct extraction and all dependent tables, figures and text')
        for start, end, field in [('2020-12', '2022-12', 'change_2020_2022'), ('2022-12', '2024-12', 'change_2022_2024')]:
            a, b = obs[start, key], obs[end, key]; s = by_source[a['source_id']]
            add(claim_id=f'B{i:02}-{end}', claim=key + ' endpoint change', evidence_class='B: arithmetic difference of observed aggregates',
                value=row[field], units='GEL million' if key.endswith('stock') else 'percentage points', period=start + ' to ' + end,
                source_url=s['url'], source_sha256=s['sha256'], source_locator=f"{a['sheet']}!{a['cell']}, {b['sheet']}!{b['cell']}",
                calculation='End minus start', uncertainty='Inherited source revisions and rounding',
                limitation='Changing portfolios, not a causal effect; FX-valued stocks include currency translation',
                counterargument='Monetary policy is not the only determinant', defensible_response='No attribution is made',
                action_if_verification_fails='Recalculate or withdraw the affected comparison')
    r = json.loads((OUT / 'results.json').read_text())
    calc = [('C01', 'Standardized new-loan monthly payment increase, Dec 2022 vs Dec 2020', r['standardized_100k_20y'][1]['change_vs_dec2020_gel'], '2020-12 to 2022-12', 'table2_standardized_new_loan.csv', 'GEL 100,000; 240 months; source annual nominal rate/12; no fees'),
            ('C02', 'Main synthetic contract additional payments', r['indexed_monthly_main']['extra_payments_48m_gel'], '2021-01 to 2024-12', 'indexed_contract_monthly.csv', 'GEL 100,000; 240 months initially; monthly start-of-month resets; policy +3pp; held 8% policy reference'),
            ('C03', 'Main synthetic contract additional interest', r['indexed_monthly_main']['extra_interest_48m_gel'], '2021-01 to 2024-12', 'indexed_contract_monthly.csv', 'Same synthetic contract; sum monthly interest differences'),
            ('C04', 'Main synthetic contract additional terminal debt', r['indexed_monthly_main']['extra_terminal_debt_gel'], '2024-12', 'indexed_contract_monthly.csv', 'Same synthetic contract; difference of closing balances'),
            ('C05', 'Main synthetic contract peak additional monthly payment', r['indexed_monthly_main']['peak_extra_monthly_payment_gel'], '2021-01 to 2024-12', 'indexed_contract_monthly.csv', 'Same synthetic contract; maximum monthly payment difference'),
            ('C06', 'Additional payments using held 9% reference', r['alternative_reference_extra_payments'], '2021-01 to 2024-12', 'alternative_reference_9pct.csv', 'Same actual-rate path; reference policy changed to 9%; same margin and maturity')]
    locks = json.loads((OUT / 'analysis_inputs.lock.json').read_text())
    for id, claim, value, period, file, assumptions in calc:
        housing = id == 'C01'; s = by_source['LMR'] if housing else old['policy_rate.xlsx']
        add(claim_id=id, claim=claim, evidence_class='C: deterministic conditional contract calculation', value=value, units='GEL', period=period,
            source_url=s.get('url', s.get('source_url')), source_sha256=s['sha256'], source_locator=file + '; src/credit_analysis.py',
            calculation=assumptions, uncertainty='Assumption sensitivity; not a statistical confidence interval',
            limitation='Not observed payments, representative borrower incidence or net policy welfare; reference is not a feasible macro counterfactual',
            counterargument='Different contracts or policy alternatives produce different amounts',
            defensible_response='Sensitivity is disclosed; no population scaling or causal claim',
            action_if_verification_fails='Correct formula/inputs and regenerate every dependent result; withdraw if contract interpretation fails')
    for i, x in enumerate(r['conditional_income_exposure'], 1):
        add(claim_id='C-income-' + str(i), claim='Peak extra payment as share of assumed income', evidence_class='C: hypothetical arithmetic illustration',
            value=x['extra_payment_income_pp'], units='percentage points of assumed monthly income', period='Synthetic 2021–2024 peak',
            source_locator='table4_conditional_income_exposure.csv', calculation=f"100 * peak_extra_payment / {x['assumed_monthly_income_gel']} GEL assumed income",
            uncertainty='Income and common debt size are assumptions', limitation='Not observed income groups or borrower eligibility',
            counterargument='Real debt and income distributions are correlated', defensible_response='No actual group incidence is inferred',
            action_if_verification_fails='Correct arithmetic or remove the illustration')
    with (OUT / 'claim_ledger.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=ledger[0].keys()); w.writeheader(); w.writerows(ledger)
    print(f'Source register and {len(ledger)} numerical claims written.')


if __name__ == '__main__':
    main()
