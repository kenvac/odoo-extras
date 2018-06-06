# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    reason_id = fields.Many2one(string="Scrap Reason",
                                comodel_name="stock.scrap.reason",
                                states={'done': [('readonly', True)]},
                                ondelete="restrict",
                                required=True,
                                help="Reason for scraping.")

    def prepare_move_values(self):
        vals = super(StockScrap, self).prepare_move_values()
        vals.update({
            'reason_id': self.reason_id.id,
        })
        return vals
