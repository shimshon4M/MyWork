# -*- coding: utf-8 -*-

import re
import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
#from cStringIO import StringIO #python2
import io #python3 not suppoted

space = re.compile(r"[  ]+")

def convert_pdf_to_txt(path, txtname, buf=True):
    rsrcmgr = PDFResourceManager()
    if buf:
        outfp = StringIO()
    else:
        outfp = open(txtname, 'w')
    codec = 'utf-8'
    laparams = LAParams()
    laparams.detect_vertical = True
    device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)

    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()
    device.close()
    if buf:
        text = re.sub(space, "", outfp.getvalue())
        print (text)
    outfp.close()

"""
引数に対象ファイル名を指定して実行
ファイル名.txtという名前でテキスト化
"""    
if __name__=="__main__":
    args=sys.argv
    convert_pdf_to_txt(args[1], args[1]+".txt",False)
