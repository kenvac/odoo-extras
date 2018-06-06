# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    reason_id = fields.Many2one(comodel_name="stock.scrap.reason",
                                states={'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]},
                                ondelete="restrict",
                                string="Scrap Reason")
