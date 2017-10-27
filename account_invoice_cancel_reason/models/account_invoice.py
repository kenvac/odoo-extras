# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    cancel_reason_id = fields.Many2one(comodel_name='invoice.cancel.reason',
                                       auto_join=True,
                                       invisible=True,
                                       required=False)

    @api.multi
    def action_cancel_draft(self):
        self.write({'cancel_reason_id': False})
        return super(AccountInvoice, self).action_cancel_draft()
