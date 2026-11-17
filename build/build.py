"""build.py - builds BO6502_Manual_IT.pdf and BO6502_Manual_EN.pdf (screen edition: cream paper,
colour pictures); with MANUAL_PRINT=1 it builds the print edition, BO6502_Manual_IT_print.pdf and _EN_print.pdf.

ReportLab lays out the text (two passes, for the index); PyMuPDF then draws the pages of the
schematics of the modules, as vectors, on the empty areas left for them (Placeholder)."""
import sys
from pathlib import Path
import pymupdf
from layout import ManualDoc, Placeholder, NextPageTemplate, Spacer, PRINT
from cover import draw_cover
from content import story, SCHEMATIC

HERE = Path(__file__).resolve().parent
OUT = HERE.parent

META = {
    'it': dict(title='BO6502 - Manuale d\'uso', subject='Manuale d\'uso del computer modulare BO6502 (W65C02S)',
               running='BO6502  MANUALE D\'USO'),
    'en': dict(title='BO6502 - Operation Manual', subject='Operation manual of the BO6502 modular computer (W65C02S)',
               running='BO6502  OPERATION MANUAL'),
}


def build(lang):
    meta = dict(META[lang], author='Boogs77', version='BIOS 16.11.26 KEYB/SD R2')
    tmp = HERE / f'_tmp_{lang}.pdf'
    dst = OUT / f'BO6502_Manual_{lang.upper()}{"_print" if PRINT else ""}.pdf'
    Placeholder.REG.clear()
    doc = ManualDoc(str(tmp), lang, meta, draw_cover(lang))
    flow = [Spacer(1, 1)] + story(lang)          # the first page uses the 'cover' template
    doc.multiBuild(flow)

    # schematic pages (one landscape sheet per module), rotated to fill the portrait areas
    pdf = pymupdf.open(tmp)
    for key, (page, x, y, w, h) in sorted(Placeholder.REG.items()):
        i = int(key[len('schem'):])
        src = pymupdf.open(SCHEMATIC[i][1])
        pg = pdf[page - 1]
        ph = pg.rect.height
        rect = pymupdf.Rect(x, ph - (y + h), x + w, ph - y)     # PDF -> PyMuPDF coordinates (top-left origin)
        pg.show_pdf_page(rect, src, 0, rotate=-90)
    pdf.save(dst, garbage=3, deflate=True)
    pdf.close()
    tmp.unlink()
    print('written', dst, doc.page, 'pages')


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['it', 'en']):
        build(lang)
