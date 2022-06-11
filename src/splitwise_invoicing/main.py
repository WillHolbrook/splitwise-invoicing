import os
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import load_env


hsbc_credit_filepath = os.getenv("HSBC_CREDIT_INVOICE_FILEPATH")


def convert_pdf_to_string(file_path):
    output_string = StringIO()
    with open(file_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        resource_manager = PDFResourceManager()
        device = TextConverter(resource_manager, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, device)
        for page in PDFPage.create_pages(doc):

            interpreter.process_page(page)

    return output_string.getvalue()


print(convert_pdf_to_string(hsbc_credit_filepath))
# reader = PdfFileReader(hsbc_credit_filepath)
# print(reader.documentInfo)
# print(reader.numPages)
# page2 = reader.getPage(1)
#
# print(page2.extract_text(space_width=50))
