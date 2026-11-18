"""Re-extract NBG quarterly information from source-pinned central forecast charts."""
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request

import numpy as np
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / 'data/derived/r3_rate_rule/vintages.csv'


def chart(page, month):
    """Read central-line vertices. Date with printed x ticks, scale with y ticks and target."""
    words = page.get_text('words')
    strokes = [d for d in page.get_drawings() if d['type'] == 's']
    curves = [d for d in strokes if d['color'] and max(d['color']) < .25
              and d['rect'].width > 100 and d['rect'].height > 4
              and len(d['items']) > 10
              and all(s[0] == 'l' and s[2].x > s[1].x for s in d['items'])]
    if len(curves) != 1:
        raise ValueError(f'{month}: ambiguous central curve')
    curve = curves[0]
    segments = curve['items']
    points = [s[1] for s in segments] + [segments[-1][2]]
    x = np.array([point.x for point in points])
    # The green line denotes the target, including the historical glide path to 3%.
    targets = [d for d in strokes if d['color'] and d['color'][1] > .6
               and d['color'][0] < .15 and abs(d['rect'].x1 - x[-1]) < 1.1*np.median(np.diff(x))
               and d['rect'].width > 50]
    target_y = targets[-1]['items'][-1][2].y
    ticks = [w for w in words if re.fullmatch(r'-?\d+%', w[4]) and 0 < x[0]-w[2] < 24]
    # Vertical axis tick labels have a common right edge. Ignore prose and legend.
    ticks = max(([z for z in ticks if abs(z[2]-w[2]) < 1.5] for w in ticks), key=len)
    levels = [int(w[4][:-1]) for w in ticks]
    centers = [(w[1]+w[3])/2 for w in ticks]
    slope, offset = np.polyfit(levels, centers, 1)
    if len(ticks) < 4 or slope >= 0 or max(abs(np.array(centers)-(slope*np.array(levels)+offset))) > 1:
        raise ValueError(f'{month}: unreadable percent axis')
    if abs((target_y-offset)/slope-3) > .25:
        raise ValueError(f'{month}: target and axis disagree')
    labels = sorted((w for w in words if re.fullmatch(r'(20\d\d)?Q[1-4]',w[4])),key=lambda w:w[0])
    first = labels[0]
    first_year = (int(first[4][:4]) if len(first[4]) > 2 else
                  int(min((w for w in words if re.fullmatch('20[0-9]{2}',w[4])
                           and first[1] < w[1] < first[3]+35), key=lambda w:w[0])[4]))
    first_index = int(np.argmin(abs(x-(first[0]+first[2])/2)))
    start = 4*first_year + int(first[4][-1])-1-first_index
    for w in labels:
        ix = np.argmin(abs(x-(w[0]+w[2])/2))
        if (start+ix)%4+1 != int(w[4][-1]):
            raise ValueError(f'{month}: quarterly alignment')
    year, m = map(int,month.split('-'))
    observed = year*4+(m-1)//3-1
    j = observed-start
    if not 0 <= j < len(points)-4:
        raise ValueError('Horizon outside chart')
    def rate(index):
        return round(float(3+(points[index].y-target_y)/slope),1)
    return dict(actual_quarter=f'{observed//4}Q{observed%4+1}',
                forecast_quarter=f'{observed//4+1}Q{observed%4+1}',
                actual_cpi_pct=rate(j),expected_cpi_pct=rate(j+4),
                path_sequence=curve['seqno'],actual_vertex=j,forecast_vertex=j+4,
                points_per_pct=round(-slope,5),target_y=round(target_y,5))


def extract(acquire):
    rows = []
    for source in json.loads((ROOT/'data/r3_rate_sources.json').read_text()):
        month = source['report_month']
        path = ROOT/'data/raw/r3_rate_rule'/f'{month}.pdf'
        if acquire and not path.exists():
            data = urllib.request.urlopen(source['url'],timeout=45).read(20_000_001)
            if len(data)>20_000_000 or hashlib.sha256(data).hexdigest()!=source['sha256']:
                raise ValueError(f'{month}: download mismatch')
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError(f'{month}: vintage hash mismatch')
        with pymupdf.open(path) as doc:
            page = doc[source['inflation_page']-1]
            printed_month = datetime.strptime(month,'%Y-%m').strftime('%B %Y')
            if printed_month not in ' '.join(page.get_text().split()):
                raise ValueError(f'{month}: date differs from printed vintage')
            gtext = ' '.join(doc[source['growth_page']-1].get_text().split())
            if source['growth_locator'] not in gtext:
                raise ValueError(f'{month}: growth locator mismatch')
            value = float(re.findall(r'-?\d+(?:\.\d+)?(?=%)',source['growth_locator'])[0])
            if 'decrease' in source['growth_locator']:
                value = -abs(value)
            if value != source['growth_pct']:
                raise ValueError(f'{month}: growth mismatch')
            rows.append(dict(report_month=month,**chart(page,month),expected_growth_pct=value))
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquire',action='store_true')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    rows = extract(args.acquire)
    buf = io.StringIO()
    writer = csv.DictWriter(buf,fieldnames=rows[0],lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    if args.check:
        assert SERIES.read_text()==buf.getvalue()
    else:
        SERIES.write_text(buf.getvalue())
