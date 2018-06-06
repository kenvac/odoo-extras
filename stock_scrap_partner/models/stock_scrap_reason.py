# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockScrapReason(models.Model):
    _inherit = 'stock.scrap.reason'

    is_partner_required = fields.Boolean(help="Tick to make partner "
                                              "field mandatory on scrap view")
