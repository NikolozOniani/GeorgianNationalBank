"""Render the review manuscript and Georgian summary; no analysis is performed here."""
import argparse
from functools import partial
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                               Image, PageBreak, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'reports/peer_review'
DEST = ROOT / 'output/pdf/Georgia_Household_Credit_Peer_Review.pdf'
BLUE = colors.HexColor('#164b68')
INK = colors.HexColor('#17232e')
PALE = colors.HexColor('#eff4f6')
WIDTH = A4[0] - 100
REPO = 'https://github.com/NikolozOniani/GeorgianNationalBank'


def inline(text):
    text = escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  lambda m: '<link href="' + escape(m[2] if m[2].startswith('https://') else REPO + '/blob/main/reports/peer_review/' + m[2], quote=True) + '" color="#164b68">' + m[1] + '</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font size="8.6">\1</font>', text)
    return text


def styles():
    body = ParagraphStyle('body', fontName='Review', fontSize=10.2, leading=14.6,
                          textColor=INK, spaceAfter=8, allowWidows=0, allowOrphans=0)
    return {'body': body,
            'h1': ParagraphStyle('h1', parent=body, fontName='ReviewBold', fontSize=21, leading=29, textColor=BLUE, spaceAfter=17, keepWithNext=True),
            'h2': ParagraphStyle('h2', parent=body, fontName='ReviewBold', fontSize=14, leading=19, textColor=BLUE, spaceBefore=13, spaceAfter=9, keepWithNext=True),
            'h3': ParagraphStyle('h3', parent=body, fontName='ReviewBold', fontSize=11.3, leading=16, spaceBefore=10, spaceAfter=7, keepWithNext=True),
            'small': ParagraphStyle('small', parent=body, fontSize=8.4, leading=11.8, spaceAfter=6),
            'cell': ParagraphStyle('cell', parent=body, fontSize=8.1, leading=11, spaceAfter=0),
            'header': ParagraphStyle('header', parent=body, fontName='ReviewBold', fontSize=8.1, leading=11, textColor=colors.white, spaceAfter=0),
            'caption': ParagraphStyle('caption', parent=body, fontSize=8.8, leading=12, textColor=BLUE, spaceAfter=12),
            'kicker': ParagraphStyle('kicker', parent=body, fontName='ReviewBold', fontSize=9, leading=13, textColor=BLUE, spaceAfter=17)}


def table(rows, st):
    n = len(rows[0]); fractions = {3: [.26, .36, .38], 4: [.30, .23, .24, .23], 5: [.40, .14, .14, .14, .18]}
    fractions = fractions.get(n, [1 / n] * n)
    data = [[Paragraph(inline(c), st['header' if i == 0 else 'cell']) for c in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=[WIDTH * x for x in fractions], repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), BLUE), ('VALIGN', (0,0), (-1,-1), 'TOP'),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, PALE]),
                           ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING', (0,0), (-1,-1), 7),
                           ('TOPPADDING', (0,0), (-1,-1), 7), ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                           ('LINEBELOW', (0,-1), (-1,-1), .5, colors.HexColor('#bacbd4'))]))
    return t


def markdown(text, st):
    lines = text.splitlines(); result = []; i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+', x) for x in row): rows.append(row)
                i += 1
            result.extend([Spacer(1, 5), table(rows, st), Spacer(1, 10)]); continue
        match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
        if match:
            img = Image(str(SOURCE / match[2])); height = WIDTH * img.imageHeight / img.imageWidth
            img.drawWidth = WIDTH; img.drawHeight = height
            result.append(KeepTogether([Spacer(1, 7), img, Paragraph(inline(match[1]), st['caption'])])); i += 1; continue
        if line.startswith('#'):
            level = min(len(line) - len(line.lstrip('#')), 3)
            result.append(Paragraph(inline(line.lstrip('#').strip()), st['h' + str(level)])); i += 1; continue
        if line.startswith('- '):
            result.append(Paragraph('• ' + inline(line[2:]), st['body'])); i += 1; continue
        para = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#', '|', '![', '- ')):
            para.append(lines[i].strip()); i += 1
        result.append(Paragraph(inline(' '.join(para)), st['body']))
    return result


def page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#bacbd4')); canvas.setLineWidth(.4)
    canvas.line(50, 42, A4[0] - 50, 42)
    canvas.setFont('Review', 7.5); canvas.setFillColor(BLUE)
    canvas.drawString(50, 29, 'GeorgianNationalBank | Credit-channel study | Review draft v0.1')
    canvas.drawRightString(A4[0] - 50, 29, str(doc.page))
    if doc.page > 1:
        canvas.setFont('Review', 7.5); canvas.setFillColor(colors.HexColor('#647684'))
        canvas.drawString(50, A4[1] - 30, 'Household credit pricing and conditional debt-service exposure, 2020–2024')
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-dir', default='/usr/share/fonts/truetype/dejavu')
    args = parser.parse_args(); fontdir = Path(args.font_dir)
    for name, file in [('Review', 'DejaVuSans.ttf'), ('ReviewBold', 'DejaVuSans-Bold.ttf'),
                       ('ReviewItalic', 'DejaVuSans-Oblique.ttf'), ('ReviewBoldItalic', 'DejaVuSans-BoldOblique.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(fontdir / file)))
    pdfmetrics.registerFontFamily('Review', normal='Review', bold='ReviewBold', italic='ReviewItalic', boldItalic='ReviewBoldItalic')
    st = styles(); manuscript = (SOURCE / 'Manuscript.md').read_text(); r = json.loads((SOURCE / 'results.json').read_text())
    story = [Spacer(1, 28), Paragraph('RESEARCH PAPER · CREDIT CHANNEL', st['kicker']),
             Paragraph('რატომ და როგორ გვაღარიბებს ეროვნული ბანკი?', st['h1']),
             Paragraph('Household credit pricing and conditional debt-service exposure in Georgia, 2020–2024', st['h2']),
             Spacer(1, 12), Paragraph('Nikoloz Oniani<br/>Discussion paper v0.1 · 8 November 2026<br/>Prepared for external methodological and substantive review', st['body']),
             Spacer(1, 18), Paragraph('A critical question, with a testable scope', st['h2']),
             Paragraph('The political title asks why and how the National Bank makes us poorer. This paper documents financing prices and conditional contract exposure. It does not establish net policy-induced impoverishment.', st['body']),
             Spacer(1, 12), table([['Evidence', 'Result', 'Interpretation'],
                                  ['Official observations', '46 monthly series; 2,760 values', 'Credit and deposit prices moved differently.'],
                                  ['Standardized loan', 'GEL 120.06 higher monthly payment', 'Assumed GEL 100,000 / 20 years, priced at Dec 2022 versus Dec 2020 housing averages.'],
                                  ['Indexed contract', 'GEL 5,933 additional payments over 2021–2024', 'Synthetic contract versus held 8% policy reference; not an observed household loss.']], st),
             Spacer(1, 18), Paragraph('Includes methods, results, three figures, limitations, source references and a Georgian summary. The accompanying repository contains the claim ledger, reviewer brief, source-cell data, executable code and tests.', st['body']),
             Paragraph('<link href="' + REPO + '/tree/main/reports/peer_review" color="#164b68">Open the replication and review packet</link>', st['small']),
             PageBreak()]
    story += markdown('## Abstract' + manuscript.split('## Abstract', 1)[1], st)
    story += [PageBreak(), Paragraph('Appendix A · Verified source downloads', st['h1']),
              Paragraph('Links below point to the official files. The accompanying source register provides the full SHA-256 hashes and byte sizes. Source vintage: 8 November 2026. The policy and IMF sources were verified in the preserved earlier work.', st['body'])]
    sources = json.loads((SOURCE / 'sources.json').read_text())
    old = json.loads((ROOT / 'reports/nbg_source_manifest.json').read_text())
    sources += [dict(id=id, title=title, url=old[key]['source_url'], sha256=old[key]['sha256'])
                for id, key, title in [('RATE', 'policy_rate.xlsx', 'Historical policy decisions and effective dates'),
                                      ('IMF2025', 'imf2025.pdf', 'Georgia: Selected Issues, Country Report 25/217')]]
    for s in sources:
        url = quote(s['url'], safe=':/?=%&')
        story.append(KeepTogether([Paragraph(escape(s['id'] + ' — ' + s['title']), st['h3']),
                                  Paragraph('<link href="' + escape(url, quote=True) + '" color="#164b68">Official source file</link> · SHA-256:', st['small']),
                                  Paragraph(s['sha256'][:32] + '<br/>' + s['sha256'][32:], st['small'])]))
    story += [PageBreak(), Paragraph('Appendix B · ქართული შეჯამება', st['h1'])]
    story += markdown((SOURCE / 'Summary_ka.md').read_text(), st)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(DEST), pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=57,
                            title='Household credit pricing and conditional debt-service exposure in Georgia, 2020–2024',
                            author='Nikoloz Oniani', subject='External review draft; descriptive and conditional analysis',
                            pageCompression=1, invariant=1)
    doc.build(story, onFirstPage=page, onLaterPages=page)
    print(DEST)


if __name__ == '__main__':
    main()
