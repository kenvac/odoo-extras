# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    scrap_ids = fields.One2many('stock.scrap', 'move_id')
