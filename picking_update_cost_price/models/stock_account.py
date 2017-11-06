# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):
        product_obj = self.env['product.product']
        for move in self:
            if (move.location_id.usage == 'supplier') and \
               (move.product_id.cost_method == 'standard'):
                ctx = dict(self._context or {},
                           force_company=move.company_id.id)
                product = product_obj.with_context(ctx).\
                    browse(move.product_id.id)
                # Write the standard price, as SUPERUSER_ID
                # because a warehouse manager may not have the
                # right to write on products
                product.sudo().write({'standard_price': move.price_unit})
        return super(StockMove, self).product_price_update_before_done()
