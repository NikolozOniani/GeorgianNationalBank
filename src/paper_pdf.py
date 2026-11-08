"""Typeset the integrated academic paper with a shared, Unicode-safe renderer."""
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
import credit_pdf as render

ROOT=Path(__file__).resolve().parents[1]


def page(canvas,doc):
    canvas.saveState();canvas.setFont('Review',7.5);canvas.setFillColor(render.BLUE)
    canvas.drawString(50,29,'Nikoloz Oniani | Monetary Sovereignty and Financial Costs | Working paper v0.2')
    canvas.drawRightString(A4[0]-50,29,str(doc.page));canvas.restoreState()


def main():
    fonts=Path('/usr/share/fonts/truetype/dejavu')
    for name,file in [('Review','DejaVuSans.ttf'),('ReviewBold','DejaVuSans-Bold.ttf'),('ReviewItalic','DejaVuSans-Oblique.ttf'),('ReviewBoldItalic','DejaVuSans-BoldOblique.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('Review',normal='Review',bold='ReviewBold',italic='ReviewItalic',boldItalic='ReviewBoldItalic')
    render.SOURCE=ROOT/'reports/paper'
    # Resolve Markdown links against the integrated paper folder rather than its supplement.
    original_inline=render.inline
    render.inline=lambda s:original_inline(s).replace('/blob/main/reports/peer_review/','/blob/main/reports/paper/')
    st=render.styles();st['body'].fontSize=10;st['body'].leading=14.2;st['body'].spaceAfter=7.5
    story=render.markdown((render.SOURCE/'Paper.md').read_text(),st)
    dest=ROOT/'output/pdf/Oniani_Monetary_Sovereignty_Georgia.pdf';dest.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(dest),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=48,bottomMargin=55,
                          title='Monetary Sovereignty, Financial Costs and Household Exposure in Georgia',author='Nikoloz Oniani',
                          subject='Academic working paper; accounting and conditional-counterfactual evidence',invariant=1)
    doc.build(story,onFirstPage=page,onLaterPages=page);print(dest)


if __name__=='__main__':main()
