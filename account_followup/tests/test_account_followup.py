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


    # def test_00_send_followup_after_3_days(self):
    #     """ Send follow up after 3 days and check nothing is done (as first follow-up level is only after 15 days)"""
    #     delta = fields.Datetime.timedelta(days=3)
    #     result = self.current_date + delta
    #     ipdb.set_trace()
    #     self.wizard_id = self.wizard.create(dict(date=result.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
    #                                              followup_id=self.followup_id
    #                                             ))
    #     self.wizard.do_process(cr, uid, [self.wizard_id], context={"followup_id": self.followup_id})
    #     self.assertFalse(self.partner.browse(cr, uid, self.partner_id).latest_followup_level_id)

    # def run_wizard_three_times(self):
    #     cr, uid = self.cr, self.uid
    #     delta = datetime.timedelta(days=40)
    #     result = self.current_date + delta
    #     result = self.current_date + delta
    #     self.wizard_id = self.wizard.create(cr, uid, {'date':result.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
    #                                                   'followup_id': self.followup_id
    #                                                   }, context={"followup_id": self.followup_id})
    #     self.wizard.do_process(cr, uid, [self.wizard_id], context={"followup_id": self.followup_id})
    #     self.wizard_id = self.wizard.create(cr, uid, {'date':result.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
    #                                                   'followup_id': self.followup_id
    #                                                   }, context={"followup_id": self.followup_id})
    #     self.wizard.do_process(cr, uid, [self.wizard_id], context={"followup_id": self.followup_id})
    #     self.wizard_id = self.wizard.create(cr, uid, {'date':result.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
    #                                                   'followup_id': self.followup_id,
    #                                                   }, context={"followup_id": self.followup_id})
    #     self.wizard.do_process(cr, uid, [self.wizard_id], context={"followup_id": self.followup_id})

    # def test_01_send_followup_later_for_upgrade(self):
    #     """ Send one follow-up after 15 days to check it upgrades to level 1"""
    #     cr, uid = self.cr, self.uid
    #     delta = datetime.timedelta(days=15)
    #     result = self.current_date + delta
    #     self.wizard_id = self.wizard.create(cr, uid, {
    #                                                   'date':result.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
    #                                                   'followup_id': self.followup_id
    #                                                   }, context={"followup_id": self.followup_id})
    #     self.wizard.do_process(cr, uid, [self.wizard_id], context={"followup_id": self.followup_id})
    #     self.assertEqual(self.partner.browse(cr, uid, self.partner_id).latest_followup_level_id.id, self.first_followup_line_id,
    #                                         "Not updated to the correct follow-up level")

    # def test_02_check_manual_action(self):
    #     """ Check that when running the wizard three times that the manual action is set"""
    #     cr, uid = self.cr, self.uid
    #     self.run_wizard_three_times()
    #     self.assertEqual(self.partner.browse(cr, uid, self.partner_id).payment_next_action,
    #                      "Call the customer on the phone! ", "Manual action not set")
    #     self.assertEqual(self.partner.browse(cr, uid, self.partner_id).payment_next_action_date,
    #                      self.current_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT))

    # def test_03_filter_on_credit(self):
    #     """ Check the partners can be filtered on having credits """
    #     cr, uid = self.cr, self.uid
    #     ids = self.partner.search(cr, uid, [('payment_amount_due', '>', 0.0)])
    #     self.assertIn(self.partner_id, ids)

    # def test_04_action_done(self):
    #     """ Run the wizard 3 times, mark it as done, check the action fields are empty"""
    #     cr, uid = self.cr, self.uid
    #     partner_rec = self.partner.browse(cr, uid, self.partner_id)
    #     self.run_wizard_three_times()
    #     self.partner.action_done(cr, uid, self.partner_id)
    #     self.assertFalse(partner_rec.payment_next_action, "Manual action not emptied")
    #     self.assertFalse(partner_rec.payment_responsible_id)
    #     self.assertFalse(partner_rec.payment_next_action_date)

    # def test_05_litigation(self):
    #     """ Set the account move line as litigation, run the wizard 3 times and check nothing happened.
    #     Turn litigation off.  Run the wizard 3 times and check it is in the right follow-up level.
    #     """
    #     cr, uid = self.cr, self.uid
    #     aml_id = self.partner.browse(cr, uid, self.partner_id).unreconciled_aml_ids[0].id
    #     self.registry('account.move.line').write(cr, uid, aml_id, {'blocked': True})
    #     self.run_wizard_three_times()
    #     self.assertFalse(self.partner.browse(cr, uid, self.partner_id).latest_followup_level_id, "Litigation does not work")
    #     self.registry('account.move.line').write(cr, uid, aml_id, {'blocked': False})
    #     self.run_wizard_three_times()
    #     self.assertEqual(self.partner.browse(cr, uid, self.partner_id).latest_followup_level_id.id,
    #                      self.last_followup_line_id, "Lines are not equal")

    # def test_06_pay_the_invoice(self):
    #     """Run wizard until manual action, pay the invoice and check that partner has no follow-up level anymore and after running the wizard the action is empty"""
    #     cr, uid = self.cr, self.uid
    #     self.test_02_check_manual_action()
    #     delta = datetime.timedelta(days=1)
    #     result = self.current_date + delta
    #     self.invoice.pay_and_reconcile(cr, uid, [self.invoice_id], 1000.0, self.pay_account_id,
    #                                          self.period_id, self.journal_id, self.pay_account_id,
    #                                          self.period_id, self.journal_id,
    #                                          name = "Payment for test customer invoice follow-up")
    #     self.assertFalse(self.partner.browse(cr, uid, self.partner_id).latest_followup_level_id, "Level not empty")
    #     self.wizard_id = self.wizard.create(cr, uid, {'date':result.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
    #                                                   'followup_id': self.followup_id
    #                                                   }, context={"followup_id": self.followup_id})
    #     self.wizard.do_process(cr, uid, [self.wizard_id], context={"followup_id": self.followup_id})
    #     self.assertEqual(0, self.partner.browse(cr, uid, self.partner_id).payment_amount_due, "Amount Due != 0")
    #     self.assertFalse(self.partner.browse(cr, uid, self.partner_id).payment_next_action_date, "Next action date not cleared")
