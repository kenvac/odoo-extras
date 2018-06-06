# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="Partner",
                                 states={'done': [('readonly', True)]},
                                 help="Used when customer samples")
    is_partner_required = fields.Boolean(invisible=True, default=False)

    @api.onchange('reason_id')
    def onchange_reason_id(self):
        self.ensure_one()
        self.is_partner_required = False
        if self.reason_id:
            self.is_partner_required = self.reason_id.is_partner_required
