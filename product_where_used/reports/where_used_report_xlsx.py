# -*- coding: utf-8 -*-
# Copyright 2019 Kinner Vachhani>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass

PO_HEADERS = ['Purchase Order',
              'PO Date',
              'Supplier',
              'Order State',
              'Product',
              'Product Code',
              'Purchase Price',
              'Quantity']

SO_HEADERS = ['Sale Order',
              'SO Date',
              'Customer',
              'Order State',
              'Product',
              'Product Code',
              'Sale Price',
              'Quantity']

BOM_HEADERS = ['Product',
               'Code',
               'Reference',
               'Quantity',
               'BOM Type'
               ]

MO_HEADERS = ['Product',
              'Code',
              'Quantity',
              'Date Planned',
              'Raw Meterial Location',
              'Finish Products Location',
              ]


class ProductXlsx(ReportXlsx):

    # _bf = xlsxwriter.Workbook().add_format({'bold': True})
    # _columnheader = xlsxwriter.Workbook().add_format({'bold': True,
    #                                                   'font_color': 'black',
    #                                                   'font_size': 10,
    #                                                   # 'center': True,
    #                                                   })

    def _write_column_headers(self, headers, sheet, column):
        ''' Headers write helper '''
        sheet.write_row(column, headers)
        # sheet.set_row(column, self._columnheader)

    def _write_row(_write_po_row, rowval, sheet, column):
        ''' Write Sheet Row '''
        sheet.write_row(column, rowval)

    def _get_po_data(self, product_ids):
        '''
            Search and return po data iterator
        '''
        sql = '''
        SELECT
            po.name as po_number,
            po.date_order as po_date,
            par.name as supplier,
            po.state,
            tmpl.name as product,
            product.default_code,
            pol.price_unit,
            pol.product_qty
        FROM purchase_order_line pol
        LEFT JOIN purchase_order po on (pol.order_id = po.id)
        LEFT JOIN res_partner par on (par.id = po.partner_id)
        LEFT JOIN product_product product on (product.id = pol.product_id)
        LEFT JOIN product_template tmpl on (tmpl.id = product.product_tmpl_id)
        WHERE po.state != 'cancel'
        AND pol.product_id IN %s
        '''
        cr = self.env.cr
        cr.execute(sql, [tuple(product_ids)])
        for record in cr.fetchall():
            yield record

    def _get_so_data(self, product_ids):
        '''
            Search and return so data iterator
        '''
        sql = '''
        SELECT
            so.name as so_number,
            so.date_order as so_date,
            par.name as customer,
            so.state,
            tmpl.name as product,
            product.default_code,
            sol.price_unit,
            sol.product_uom_qty as product_qty
        FROM sale_order_line sol
        LEFT JOIN sale_order so on (sol.order_id = so.id)
        LEFT JOIN res_partner par on (par.id = so.partner_id)
        LEFT JOIN product_product product on (product.id = sol.product_id)
        LEFT JOIN product_template tmpl on (tmpl.id = product.product_tmpl_id)
        WHERE so.state != 'cancel'
        AND sol.product_id IN %s
        '''
        cr = self.env.cr
        cr.execute(sql, [tuple(product_ids)])
        for record in cr.fetchall():
            yield record

    def _get_bom_data(self, product_ids):
        '''
            Search and return bom data iterator
        '''
        products = self.env['product.product'].browse(product_ids)
        product_template_ids = products._get_name_template_ids()
        sql = '''
        SELECT
            tmpl.name,
            product.default_code,
            bom.type,
            bom.code AS reference,
            bom.product_qty
        FROM mrp_bom AS bom
        LEFT JOIN product_template tmpl ON (tmpl.id = bom.product_tmpl_id)
        LEFT JOIN product_product product
            ON (tmpl.id = product.product_tmpl_id)
        WHERE bom.product_tmpl_id IN %s
        '''
        cr = self.env.cr
        cr.execute(sql, [tuple(product_template_ids)])
        for record in cr.fetchall():
            yield record

    def _get_mo_data(self, product_ids):
        '''
            Search and return MO data iterator
        '''
        # products = self.env['product.product'].browse(product_ids)
        # product_template_ids = products._get_name_template_ids()
        sql = '''
        SELECT
            tmpl.name,
            product.default_code,
            mrp.product_qty,
            mrp.date_planned,
            raw_loc.complete_name AS raw_loc,
            fin_loc.complete_name AS fin_loc,
            mrp.state
        FROM mrp_production mrp
        LEFT JOIN product_product product ON (product.id = mrp.product_id)
        LEFT JOIN product_template tmpl ON (tmpl.id = product.product_tmpl_id)
        LEFT JOIN stock_location raw_loc ON (raw_loc.id = mrp.location_src_id)
        LEFT JOIN stock_location fin_loc ON (fin_loc.id = mrp.location_dest_id)
        WHERE mrp.state NOT IN ('cancel', 'draft')
        AND mrp.product_id IN %s
        '''
        cr = self.env.cr
        cr.execute(sql, [tuple(product_ids)])
        for record in cr.fetchall():
            yield record

    def generate_xlsx_report(self, workbook, data, products):
        headerFormat = workbook.add_format({'bold': True,
                                            'font_color': 'Blue',
                                            'font_size': 12,
                                            'align': 'center',
                                            })
        search_product = 'Search Product:' + data.get('product_name')
        type = data.get('type', '')
        product_ids = data.get('product_ids', [])
        if 'purchase' in type or 'all' in type:
            # Add purchase order sheet
            po_sheet = workbook.add_worksheet('Purchase Order')
            po_sheet.set_column('A:H', 15)
            row = 5
            column = 0
            po = self._get_po_data(product_ids)
            po_sheet.merge_range('A2:H2', 'Purchased Order', headerFormat)
            po_sheet.merge_range('A3:B3', search_product)
            # po_sheet.write('A3', search_product)
            self._write_column_headers(
                PO_HEADERS, po_sheet, 'A'+str(row))
            row += 1
            # Data Write
            for index, datarow in enumerate(po):
                self._write_row(datarow, po_sheet, 'A'+str(row+index))
        if 'sales' in type or 'all' in type:
            # Add Sale order sheet
            so_sheet = workbook.add_worksheet('Sale Order')
            so_sheet.set_column('A:H', 15)
            row = 5
            column = 0
            so = self._get_so_data(product_ids)
            so_sheet.merge_range('A2:H2', 'Sale Order', headerFormat)
            so_sheet.merge_range('A3:B3', search_product)
            self._write_column_headers(SO_HEADERS, so_sheet, 'A'+str(row))
            row += 1
            # Data Write
            for index, datarow in enumerate(so):
                self._write_row(datarow, so_sheet, 'A'+str(row+index))
        if 'bom' in type or 'all' in type:
            # Add BOM sheet
            bom_sheet = workbook.add_worksheet('Bills of Material')
            bom_sheet.set_column('A:E', 15)
            row = 5
            column = 0
            bom = self._get_bom_data(product_ids)
            bom_sheet.merge_range('A2:H2', 'Bills of Materials', headerFormat)
            bom_sheet.merge_range('A3:B3', search_product)
            self._write_column_headers(BOM_HEADERS, bom_sheet, 'A'+str(row))
            row += 1
            # Data Write
            for index, datarow in enumerate(bom):
                self._write_row(datarow, bom_sheet, 'A'+str(row+index))
        if 'mo' in type or 'all' in type:
            # Add MO sheet
            mo_sheet = workbook.add_worksheet('Manufacturing Order')
            mo_sheet.set_column('A:G', 15)
            row = 5
            mo = self._get_mo_data(product_ids)
            mo_sheet.merge_range('A2:H2', 'Manufacturing Order', headerFormat)
            mo_sheet.merge_range('A3:B3', search_product)
            self._write_column_headers(MO_HEADERS, mo_sheet, 'A'+str(row))
            row += 1
            # Data Write
            for index, datarow in enumerate(mo):
                self._write_row(datarow, mo_sheet, 'A'+str(row+index))


ProductXlsx('report.product.product.xlsx', 'product.product')
