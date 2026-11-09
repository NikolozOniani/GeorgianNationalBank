"""Focused regressions for acquisition safety and empirical definitions."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from src import acquire_episode as acquire

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/derived/episode_2026_11_09'


def rows(name):
    with (DATA/(name+'.csv')).open() as file:return list(csv.DictReader(file))


class AcquisitionSafety(unittest.TestCase):
    def zip_bytes(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_STORED) as z:
            z.writestr('xl/workbook.xml','<workbook>ORIGINAL</workbook>')
        return b.getvalue()

    def test_crc_none_is_success(self):
        self.assertIsNone(acquire.validate_bytes(self.zip_bytes(),'xlsx'))

    def test_bad_crc_rejected(self):
        bad=self.zip_bytes().replace(b'ORIGINAL',b'ALTEREDD')
        with self.assertRaises((ValueError,zipfile.BadZipFile)):acquire.validate_bytes(bad,'xlsx')

    def test_malformed_zip_rejected(self):
        with self.assertRaises(zipfile.BadZipFile):acquire.validate_bytes(b'not a ZIP','xlsx')

    def test_partial_failure_preserves_success_and_pin(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);raw=p/'raw';raw.mkdir();manifest=p/'manifest.json'
            original=b'{"actual":17}'; (raw/'good.json').write_bytes(original);(raw/'bad.json').write_bytes(b'broken')
            pin=hashlib.sha256(original).hexdigest()
            manifest.write_text(json.dumps([dict(id='old',status='acquired',sha256='oldpin'),dict(id='bad',status='failed',expected_sha256=pin)]))
            plan=[dict(id=n,format='json',url='https://example.invalid/not-used') for n in ['good','bad']]
            with patch.object(acquire,'RAW',raw),patch.object(acquire,'ROOT',p),patch.object(acquire,'MANIFEST',manifest):
                result=acquire.acquire(plan)
            self.assertEqual(result['good']['status'],'acquired')
            self.assertEqual(result['bad']['status'],'failed')
            self.assertEqual(result['bad']['expected_sha256'],pin)
            self.assertEqual(result['old']['sha256'],'oldpin')
            self.assertEqual((raw/'good.json').read_bytes(),original)

    def test_changed_cache_cannot_reset_pin(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);(p/'x.json').write_text('{"changed":true}')
            item=dict(id='x',format='json',url='https://example.invalid/not-used')
            with patch.object(acquire,'RAW',p),patch.object(acquire,'ROOT',p):
                r=acquire.fetch(item,dict(status='failed',expected_sha256='0'*64))
            self.assertEqual(r['status'],'failed');self.assertEqual(r['expected_sha256'],'0'*64)

    def test_known_large_file_never_requested(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            with patch.object(acquire,'RAW',p),patch.object(acquire,'ROOT',p),patch.object(acquire.urllib.request,'urlopen') as request:
                r=acquire.fetch(dict(id='large',format='xlsx',url='https://example.invalid/large',bytes=2_000_000,sha256='0'*64))
            request.assert_not_called()
            self.assertEqual(r['status'],'failed')
            self.assertIn('Manual acquisition required',r['error'])


class EmpiricalDefinitions(unittest.TestCase):
    def test_net_does_not_manufacture_gross(self):
        data=rows('intervention_monthly')
        self.assertTrue(all(r['nonauction_gross_purchases_usdm']==r['nonauction_gross_sales_usdm']=='' for r in data))
        march=next(r for r in data if r['month']=='2026-03')
        self.assertEqual(float(march['nonauction_net_purchases_usdm']),-16.2)
        self.assertAlmostEqual(sum(float(r['net_market_purchases_usdm']) for r in data if r['month'].startswith('2025')),2432.5)

    def test_units_and_weekend_are_not_fake_trades(self):
        d={r['date']:r for r in rows('official_fx_daily')}
        self.assertEqual(len(d),2505)
        self.assertAlmostEqual(float(d['2024-12-31']['usd_gel']),2.8068)
        self.assertAlmostEqual(float(d['2025-12-31']['usd_gel']),2.6951)
        mapping=rows('fx_quote_conventions')
        self.assertTrue(all(float(r['quoted_units'])==1000 for r in mapping if r['currency']=='AMD'))

    def test_monthly_window_and_missing_disclosures(self):
        with (ROOT/'reports/acquisition_2026_11_09/monthly_policy_panel.csv').open() as file:d=list(csv.DictReader(file))
        self.assertEqual(len(d),82);self.assertEqual(d[-1]['month'],'2026-10')
        self.assertEqual(d[-1]['net_market_purchases_usdm'],'')
        self.assertTrue(all(r['government_fx_conversions_usdm']=='' and r['identified_fx_valuation_usdm']=='' for r in d))

    def test_sparse_reserve_cells_not_zero_filled(self):
        d=rows('reserve_liquidity_reported')
        catalogue=json.loads((DATA/'catalogue.json').read_text())
        full=next(r for r in catalogue if r['file'].endswith('/reserve_liquidity_cells.csv'))
        self.assertGreater(full['missing_cells']['value'],0)
        self.assertTrue(any(r['source_value_status']=='reported' and float(r['value'])==0 for r in d))

    def test_known_source_problems_are_retained(self):
        bad=next(r for r in rows('fx_market_monthly') if r['month']=='2026-02' and r['bank_side']=='bank_sell')
        self.assertAlmostEqual(float(bad['total_minus_reported_components_usdm']),-522.66170405)
        malformed=[r for r in rows('government_external_debt_monthly') if r['source_date_label']=='31.06.2025']
        self.assertEqual(len(malformed),4);self.assertTrue(all(r['date']=='' and r['month']=='2025-06' for r in malformed))
        self.assertEqual(len([r for r in rows('money_transfers_canonical') if r['date'].startswith('2024')]),24)

    def test_validation_does_not_hide_qualifications(self):
        r=json.loads((ROOT/'reports/acquisition_2026_11_09/validation.json').read_text())
        self.assertTrue(r['required_checks_passed']);self.assertFalse(r['all_checks_passed'])
        failed={x['check'] for x in r['checks'] if not x['passed']}
        self.assertEqual(failed,{'dated_auction_vs_monthly','money_market_security_total','transfer_workbook_overlap'})
        self.assertFalse(r['causal_estimation_performed'])

    def test_no_unreconstructed_ara_claim(self):
        with (ROOT/'reports/acquisition_2026_11_09/ara_component_inputs.csv').open() as file:r=list(csv.DictReader(file))
        self.assertTrue(all(x['short_term_debt_residual_maturity_usdm']==x['independently_reconstructed_ara']=='' for x in r))
        y=next(x for x in r if x['year']=='2025')
        self.assertAlmostEqual(float(y['imf_published_ara_ratio'])*100,94.85332607)
        self.assertEqual(float(y['nbg_reported_ara_pct']),104.8)


if __name__=='__main__':unittest.main()
