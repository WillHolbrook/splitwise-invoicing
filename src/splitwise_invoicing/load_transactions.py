import logging
import os
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import NamedStyle
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet.datavalidation import DataValidation

from splitwise_invoicing.load_env import environment
from splitwise_invoicing.invoice_extraction import load_hsbc_credit_transaction_data

hsbc_path = Path(os.getenv("HSBC_CREDIT_INVOICE_FILEPATH")).resolve()
received_dates, transaction_dates, details, amounts = [], [], [], []

for invoice_path in sorted(hsbc_path.iterdir()):
    result_tuple = load_hsbc_credit_transaction_data(invoice_path)
    received_dates += result_tuple[0]
    transaction_dates += result_tuple[1]
    details += result_tuple[2]
    amounts += result_tuple[3]

template_xl_path = Path(os.getenv("TEMPLATE_XL_PATH"))
transaction_sheet_name = os.getenv("TRANSACTION_SHEET_NAME")
config_sheet_name = os.getenv("CONFIG_SHEET_NAME")
received_date_column_name = os.getenv("RECEIVED_DATE_COLUMN_NAME")
transaction_date_column_name = os.getenv("TRANSACTION_DATE_COLUMN_NAME")
details_column_name = os.getenv("DETAILS_COLUMN_NAME")
amount_column_name = os.getenv("AMOUNT_COLUMN_NAME")
exact_match_column_name = os.getenv("EXACT_MATCH_COLUMN_NAME")
partial_match_column_name = os.getenv("PARTIAL_MATCH_COLUMN_NAME")
partial_match_category_column_name = os.getenv("PARTIAL_MATCH_CATEGORY_COLUMN_NAME")
group_column_name = os.getenv("GROUP_COLUMN_NAME")
add_to_splitwise_column_name = os.getenv("ADD_TO_SPLITWISE_COLUMN_NAME")
adding_default = os.getenv("ADDING_DEFAULT").lower() == "true"
ascii_uppercase_offset = 64

add_to_splitwise_data_validation = DataValidation(type="list", formula1='"TRUE,FALSE"', allow_blank=False)
date_format = NamedStyle("date_format", number_format="d mmmm yyyy")
currency_format = NamedStyle("currency_format", number_format="£#,###.00;[Red]£-#,###.00;0.00")

logging.info(f"Environment: {environment}")

template_xl: Workbook = load_workbook(template_xl_path)
transaction_sheet: Worksheet = template_xl[transaction_sheet_name]
config_sheet: Worksheet = template_xl[config_sheet_name]

transaction_column_dict = {}

column_number = 1
for column in transaction_sheet.iter_cols(1, transaction_sheet.max_column):
    transaction_column_dict[column[0].value] = column_number
    column_number += 1


def write_list_to_column(sheet: Worksheet, column_index: int, values: list, format: NamedStyle | None = None) -> None:
    row_num = 2
    for value in values:
        current_cell = sheet.cell(row=row_num, column=column_index)
        current_cell.value = value
        if format:
            current_cell.style = format

        row_num += 1


num_transactions = len(transaction_dates)

default_group = config_sheet.cell(2, 1).value
write_list_to_column(transaction_sheet, transaction_column_dict[group_column_name], [default_group] * num_transactions)

write_list_to_column(transaction_sheet, transaction_column_dict[add_to_splitwise_column_name], [adding_default] * num_transactions)
write_list_to_column(transaction_sheet, transaction_column_dict[transaction_date_column_name], transaction_dates, date_format)
write_list_to_column(transaction_sheet, transaction_column_dict[received_date_column_name], received_dates, date_format)
write_list_to_column(transaction_sheet, transaction_column_dict[details_column_name], details)
write_list_to_column(transaction_sheet, transaction_column_dict[amount_column_name], amounts, currency_format)

add_to_splitwise_column_letter = chr(transaction_column_dict[add_to_splitwise_column_name] + ascii_uppercase_offset)
add_to_splitwise_data_validation.add(f'{add_to_splitwise_column_letter}2:{add_to_splitwise_column_letter}1048576')
transaction_sheet.add_data_validation(add_to_splitwise_data_validation)

template_xl.save(f"SplitwiseInvoicing-{str(datetime.now()).replace(':', '.')}.xlsx")
