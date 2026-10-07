"""Render the source-controlled scientific report and live result tables."""
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/pdf/zenithsync-technical-report.pdf'
INK = colors.HexColor('#132B37')
TEAL = colors.HexColor('#087F83')
MUTED = colors.HexColor('#526571')
STYLE = ParagraphStyle('body', fontName='Helvetica', fontSize=10.6, leading=15.8,
                       textColor=INK, spaceAfter=12, splitLongWords=True)
TITLE = ParagraphStyle('title', parent=STYLE, fontName='Helvetica-Bold', fontSize=23,
                       leading=28, textColor=INK, spaceAfter=18)
SUBTITLE = ParagraphStyle('subtitle', parent=STYLE, fontSize=14, leading=19, textColor=TEAL, spaceAfter=20)
CELL = ParagraphStyle('cell', parent=STYLE, fontSize=9.5, leading=13, spaceAfter=0)
HEADER = ParagraphStyle('header', parent=CELL, textColor=colors.white, fontName='Helvetica-Bold')


def text(value):
    return escape(value).replace('`', '')


def table(rows, widths):
    value=Table([[Paragraph(text(str(v)), HEADER if i==0 else CELL) for v in row]
                 for i,row in enumerate(rows)], colWidths=widths, hAlign='LEFT')
    value.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#EEF5F4'),colors.white]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),9),
        ('RIGHTPADDING',(0,0),(-1,-1),9)]))
    return [value,Spacer(1,16)]


def furniture(canvas, doc):
    width,height=A4
    canvas.saveState()
    canvas.setStrokeColor(TEAL);canvas.setLineWidth(1.4)
    canvas.line(48,height-38,width-48,height-38)
    canvas.setFont('Helvetica-Bold',8);canvas.setFillColor(MUTED)
    canvas.drawString(48,height-28,'ZENITHSYNC  /  TECHNICAL REPORT')
    canvas.setFont('Helvetica',8)
    canvas.drawString(48,28,'Research candidate | 6 October 2026 | Public-data evidence')
    canvas.drawRightString(width-48,28,str(doc.page))
    canvas.restoreState()


def main():
    source=(ROOT/'docs/30-technical-report.md').read_text()
    if not source.isascii():
        raise ValueError('Report source must use supported ASCII glyphs')
    result=json.loads((ROOT/'artifacts/kryeziu_confirmation_v1/confirmation.json').read_text())['orientations']['p1_to_p2']
    assert round(result['relative_reduction']*100,2)==32.82
    assert round(result['efficiency_secondary']['mse_ratio'],5)==.89185
    labels={'exact_joint':'Exact / joint GP','greedy_joint':'Greedy / joint GP',
        'exact_diagonal':'Exact / diagonal GP','random_pchip':'Random / PCHIP',
        'random_linear':'Random / linear','random_joint':'Random / joint GP','random_diagonal':'Random / diagonal GP'}
    result_rows=[['Method','Mean-budget MSE']]+[[v,f"{result['mean_budget_mse'][k]:.6f}"] for k,v in labels.items()]
    cost_rows=[['Full pool','Random wells','Exact wells','Contexts'],[18,14,11,3590],[22,17,13,2515],
               [21,16,12,231],[15,12,9,86],[19,15,12,74]]
    story=[]
    sections=source.split('---PAGE---')
    for i,section in enumerate(sections):
        if i: story.append(PageBreak())
        for block in re.split(r'\n\s*\n',section.strip()):
            if block=='[[RESULTS_TABLE]]':story.extend(table(result_rows,[344,155]))
            elif block=='[[COST_TABLE]]':story.extend(table(cost_rows,[110,130,130,129]))
            elif block.startswith('# '):
                for line in block.splitlines():
                    story.append(Paragraph(text(line.lstrip('# ')),SUBTITLE if line.startswith('## ') else TITLE))
            else:story.append(Paragraph(text(block.replace('\n',' ')),STYLE))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=58,bottomMargin=50,
                         title='ZenithSync Assay Planner: control-aware finite-well design',author='Shengbo Jiang | ZenithSync',
                         subject='Frozen public-cohort confirmation and bounded research workflow')
    doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
    print(OUT)


if __name__=='__main__':main()
