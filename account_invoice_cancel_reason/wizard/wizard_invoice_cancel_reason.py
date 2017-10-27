# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class WizardInvoiceCancelReason(models.TransientModel):
    _name = 'wizard.invoice.cancel.reason'

    def _get_type(self):
        return self._context.get('type', False)

    cancel_reason_id = fields.Many2one('invoice.cancel.reason')
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund')], default=_get_type)

    @api.multi
    def post(self):
        context = self._context
        if context.get('active_model') == 'account.invoice' and \
           context.get('active_ids'):
            invoices = self.env['account.invoice'].\
                browse(context.get('active_ids'))
            invoices.cancel_reason_id = self.cancel_reason_id.id
            invoices.signal_workflow('invoice_cancel')

        return {
            'type': 'ir.actions.act_window_close',
        }
