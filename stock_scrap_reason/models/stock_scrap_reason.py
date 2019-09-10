# Copyright 2019 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockScrapReason(models.Model):
    _name = 'stock.scrap.reason'
    _description = 'Scrap Reason'

    name = fields.Char(required=True)
