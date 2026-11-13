from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from native_math import rich_text

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT
doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.top_margin = Inches(.72)
section.bottom_margin = Inches(.72)
section.left_margin = Inches(.8)
section.right_margin = Inches(.8)
section.header_distance = Inches(.3)
section.footer_distance = Inches(.3)

for name in ['Normal', 'Title', 'Heading 1', 'Heading 2', 'Caption']:
    style = doc.styles[name]
    style.font.name = 'Arial'
    style.font.color.rgb = RGBColor(0,0,0)
normal=doc.styles['Normal']
normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.06
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
doc.styles['Title'].font.size=Pt(19)
doc.styles['Title'].font.bold=True
doc.styles['Title'].paragraph_format.space_after=Pt(12)
doc.styles['Heading 1'].font.size=Pt(13)
doc.styles['Heading 1'].font.bold=True
doc.styles['Heading 1'].paragraph_format.space_before=Pt(14)
doc.styles['Heading 1'].paragraph_format.space_after=Pt(7)
doc.styles['Caption'].font.size=Pt(9)
doc.styles['Caption'].font.italic=False
doc.styles['Caption'].font.bold=False
doc.styles['Caption'].paragraph_format.space_after=Pt(10)
doc.styles['Caption'].paragraph_format.line_spacing=1.05


# Remove inherited theme fonts and paragraph decoration from the default template.
for style in doc.styles:
    for rf in style.element.findall('.//' + qn('w:rFonts')):
        for attr in ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme', 'csTheme']:
            rf.attrib.pop(qn('w:' + attr), None)
    for border in list(style.element.findall('.//' + qn('w:pBdr'))):
        border.getparent().remove(border)
for style_name in ['Normal', 'Title', 'Heading 1', 'Heading 2', 'Caption']:
    rf=doc.styles[style_name].element.get_or_add_rPr().get_or_add_rFonts()
    for script in ['ascii','hAnsi','eastAsia','cs']:
        rf.set(qn('w:' + script),'Arial')

header=section.header.paragraphs[0]
header.text='QXU6028  |  Polymer Devices  |  2026-27'
header.runs[0].font.size=Pt(8)
footer=section.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple')
field.set(qn('w:instr'),'PAGE')
footer._p.append(field)

text=(PACKAGE/'report.md').read_text()
current_section=''
for block in text.strip().split('\n\n'):
    if block.startswith('# '):
        doc.add_paragraph(block[2:],'Title')
    elif block.startswith('## '):
        current_section=block[3:]
        heading=doc.add_paragraph(current_section,'Heading 1')
        if current_section=='References': heading.paragraph_format.page_break_before=True
    elif block.startswith('!['):
        match=re.search(r'!\[(.*?)\]\((.*?)\)',block)
        p=doc.add_paragraph()
        p.paragraph_format.space_after=Pt(4)
        p.paragraph_format.keep_with_next=True
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        shape=p.add_run().add_picture(str(PACKAGE/match[2]),width=Inches(6.5))
        shape._inline.docPr.set('descr',match[1])
    elif block.startswith('*Figure'):
        p=doc.add_paragraph(style='Caption')
        rich_text(p,block.strip('*'))
    else:
        p=doc.add_paragraph()
        rich_text(p,block)
        if current_section=='Transfer to a polymer field effect transistor':
            p.paragraph_format.keep_together=True
        if block.startswith('['):
            p.paragraph_format.space_after=Pt(5)
            for run in p.runs: run.font.size=Pt(9)
        if block.startswith('Group number') or block.startswith('Student names') or block.startswith('____'):
            p.paragraph_format.space_after=Pt(8)
doc.core_properties.title='Electrical characterisation of a graphene wafer'
doc.core_properties.subject='QXU6028 virtual laboratory coursework'
doc.core_properties.author=''
doc.core_properties.keywords='carrier counting, mobility, density of states, inverse problem'
mathpr=doc.settings.element.find(qn('m:mathPr'))
if mathpr is None:
    mathpr=OxmlElement('m:mathPr');doc.settings.element.append(mathpr)
mathfont=mathpr.find(qn('m:mathFont'))
if mathfont is None:
    mathfont=OxmlElement('m:mathFont');mathpr.append(mathfont)
mathfont.set(qn('m:val'),'Arial')
doc.save(ROOT/'QXU6028_Coursework_Report.docx')

words=len(re.sub(r'!\[.*?\]\(.*?\)','',text).split())
print('Saved report. Conservative whitespace word count including captions and references:',words)
