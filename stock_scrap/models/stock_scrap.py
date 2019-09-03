# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, api, fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.depends('scrap_qty', 'product_id', 'cost')
    def _compute_total_cost(self):
        for record in self:
            if record.product_id:
                record.total_cost = (record.scrap_qty or 0.0) * record.cost
            else:
                record.total_cost = record.cost = 0.0

    cost = fields.Float('Unit Cost Price', default=0.0,
                        states={'done': [('readonly', True)]},
                        help="Cost Price per unit")
    total_cost = fields.Float(help="""Total Scap Total. Total """
                                   """Scrap quantity * Unit Cost price""",
                              compute=lambda self: self._compute_total_cost(),
                              store=True)

    @api.onchange('cost', 'scrap_qty')
    def _onchange_cost(self):
        if self.product_id:
            self.total_cost = self.scrap_qty * self.cost

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.total_cost = self.cost = 0.0
        if self.product_id:
            self.cost = self.product_id.standard_price
            self.total_cost = self.scrap_qty * self.cost
