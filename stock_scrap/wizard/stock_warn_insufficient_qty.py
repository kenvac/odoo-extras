# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models


class StockWarnInsufficientQty(models.AbstractModel):
    _name = 'stock.warn.insufficient.qty'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    location_id = fields.Many2one('stock.location', 'Location',
                                  domain="[('usage', '=', 'internal')]",
                                  required=True)
    quant_ids = fields.Many2many('stock.quant', compute='_compute_quant_ids')

    @api.depends('product_id')
    def _compute_quant_ids(self):
        self.ensure_one()
        self.quant_ids = self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id.usage', '=', 'internal')
        ])

    @api.multi
    def action_done(self):
        raise NotImplementedError()


class StockWarnInsufficientQtyScrap(models.TransientModel):
    _name = 'stock.warn.insufficient.qty.scrap'
    _inherit = 'stock.warn.insufficient.qty'

    scrap_id = fields.Many2one('stock.scrap', 'Scrap')

    @api.multi
    def action_done(self):
        return self.scrap_id.do_scrap()
