# -*- coding: utf-8 -*-
# Copyright 2019 Kinner Vachhani>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class WizarWhereUsedRepor(models.TransientModel):
    _name = 'wizard.where.used.report'
    _description = 'Prododuct where used report wizard'

    product_id = fields.Many2one(
        comodel_name='product.product', string="Product")
    type = fields.Selection(
        selection=[('purchase', 'Purchase'),
                   ('sales', 'Sales'),
                   ('bom', 'Bills of Material'),
                   ('mo', 'Manufacturing Order'),
                   ('all', 'All')], string='Report Type',
        default=lambda self: 'all',
        required=1,
        help="""Purchase: Report purchase order with product and it's used bom
        Sales: Report all sales order with product and it's used bom
        Bills of Material: Report of all boms that use selected product
        All: Include all sales, purchase and bom in report"""
    )

    # Use Case 1 - Product 1
    # Product 1
    #   product 2
    # Use Case 2 - Product 2
    # Product 1
    #   product 2
    # Use Case 3 - Product 3
    # Product 1
    #   product 2
    #       product 3
    # Use Case 4 - No bom or bom line

    @api.multi
    def button_confirm(self):
        '''Wizard button confirm method'''

        # Get bom lines and find all the parent bom product_templ or product_id
        product_ids = self.get_bom_parents(self.product_id)

        # You got all the product ids to look for
        # Search for all po lines
        # Search for sales order

        # partners = self.env['res.partner'].browse(7)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'product.product.xlsx',
                'datas': {'product_ids': product_ids, 'type': self.type,
                          'product_name': self.product_id.name},
                'ids': product_ids}
        # return True

    def _get_all_parents(self, bom_line):
        bom = bom_line.bom_id
        if bom.product_id:
            product_ids = [bom.product_id.id]
        else:
            product_template = bom.product_tmpl_id
            products = self.env['product.product'].search(
                [('product_tmpl_id', '=', product_template.id)])
            product_ids = products.ids
        bom_lines = bom_line.search([('product_id', 'in', product_ids)])

        for bline in bom_lines:
            product_ids.extend(self._get_all_parents(bline))
        return product_ids

    def get_bom_parents(self, product_id):
        ''' Get all parent boms at from all level
            E.g Product 1
                    Product 2
                        product 3
            returns [product_1, product2, product3]
        '''
        product_ids = [self.product_id.id]
        MRP_BOM_LINE = self.env['mrp.bom.line']
        bom_lines = MRP_BOM_LINE.search(
            [('product_id', '=', self.product_id.id)])
        for line in bom_lines:
            product_ids.extend(self._get_all_parents(line))
        return product_ids
