# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class StockValuationXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, products):
        sheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        sheet.write(0, 0, "Product Name", bold)
        sheet.write(0, 1, "Product Code", bold)
        sheet.write(0, 2, "Seller", bold)
        sheet.write(0, 3, "Unit Cost", bold)
        sheet.write(0, 4, "Qty on hand", bold)
        sheet.write(0, 5, "Valuation", bold)

        row = 1
        for obj in data['form']:
            # One sheet by partner
            sheet.write(row, 0, obj['name'])
            sheet.write(row, 1, obj['code'])
            sheet.write(row, 2, obj['seller'])
            sheet.write(row, 3, obj['cost'])
            sheet.write(row, 4, obj['qty'])
            sheet.write(row, 5, obj['valuation'])
            row += 1


StockValuationXlsx('report.stock.valuation.xlsx', 'product.product')
