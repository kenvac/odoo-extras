# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# Copyright 2018 Access Bookings Ltd (https://accessbookings.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields


class TestAccountFollowup(TransactionCase):
    def setUp(self):
        """ setUp ***"""
        super(TestAccountFollowup, self).setUp()
        self.user = self.env['res.users']
        self.user_id = self.user
        self.partner = self.env['res.partner']
        self.invoice = self.env['account.invoice']
        self.invoice_line = self.env['account.invoice.line']
        self.wizard = self.env['account_followup.print']
        self.followup_id = self.env['account_followup.followup']

        self.partner_id = self.partner.create({'name': 'Test Company',
                                               'email': 'test@localhost',
                                               'is_company': True,
                                               })
        self.followup_id = self.ref('account_followup.demo_followup1')
        self.account_id = self.ref('account.data_account_type_receivable')
        self.journal_id = self.env['account.journal'].search([('type', '=',
                                                               'sale')],
                                                             limit=1)
        self.pay_account_id = self.env['account.journal'].search([
            ('type', '=', 'bank')], limit=1)
        # self.period_id = self.ref("account.period_10")
        self.first_followup_line_id = self.ref(
            "account_followup.demo_followup_line1")
        self.last_followup_line_id = self.ref(
            "account_followup.demo_followup_line3")
        self.product_id = self.ref("product.product_product_6")
        self.account_user_type = self.env.ref(
            'account.data_account_type_receivable')
        invoice_line_data = [
            (0, 0,
                {
                    'name': "LCD Screen",
                    'product_id': self.product_id,
                    'quantity': 5,
                    'price_unit': 200,
                    'account_id': self.env['account.account'].search([
                        ('user_type_id', '=', self.env.ref(
                            'account.data_account_type_revenue').id)],
                        limit=1).id,
                }
             )
        ]
        self.invoice_id = self.invoice.create(dict(
            partner_id=self.partner_id.id,
            account_id=self.account_id,
            journal_id=self.journal_id.id,
            invoice_line_ids=invoice_line_data
        ))

        # Confirm the invoice
        self.invoice_id.action_invoice_open()

        # self.voucher = self.env["account.voucher"]
        self.current_date = fields.Date.context_today()
