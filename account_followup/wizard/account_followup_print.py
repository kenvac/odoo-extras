# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# Copyright 2018 Access Bookings Ltd (https://accessbookings.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time
import datetime

from odoo import tools
from odoo import fields, models, api


class AccountFollowupStatByPartner(models.Model):
    _name = "account_followup.stat.by.partner"
    _description = "Follow-up Statistics by Partner"
    _rec_name = 'partner_id'
    _auto = False

    # Compute fields
    @api.multi
    @api.depends('partner_id')
    def _compute_invoice_partner_id(self):
        for rec in self:
            rec.invoice_partner_id = rec.partner_id.address_get(['invoice'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr,
                                  'account_followup_stat_by_partner')
        # Here we don't have other choice but to create a virtual ID based on the concatenation
        # of the partner_id and the company_id, because if a partner is shared between 2 companies,
        # we want to see 2 lines for him in this table. It means that both company should be able
        # to send him follow-ups separately . An assumption that the number of companies will not
        # reach 10 000 records is made, what should be enough for a time.
        self.env.cr.execute("""
            create view account_followup_stat_by_partner as (
                SELECT
                    l.partner_id * 10000::bigint + l.company_id as id,
                    l.partner_id AS partner_id,
                    min(l.date) AS date_move,
                    max(l.date) AS date_move_last,
                    max(l.followup_date) AS date_followup,
                    max(l.followup_line_id) AS max_followup_id,
                    sum(l.debit - l.credit) AS balance,
                    l.company_id as company_id
                FROM
                    account_move_line l
                    LEFT JOIN account_account a ON (l.account_id = a.id)
                WHERE
                    a.deprecated is not False AND
                    a.internal_type = 'receivable' AND
                    l.full_reconcile_id is NULL AND
                    l.partner_id IS NOT NULL
                    GROUP BY
                    l.partner_id, l.company_id
            )""")

    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    date_move = fields.Date('First move', readonly=True)
    date_move_last = fields.Date('Last move', readonly=True)
    date_followup = fields.Date('Latest follow-up', readonly=True)
    max_followup_id = fields.Many2one('account_followup.followup.line',
                                      'Max Follow Up Level', readonly=True,
                                      ondelete="cascade")
    balance = fields.Float(readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    invoice_partner_id = fields.Many2one(compute="_compute_invoice_partner_id",
                                         comodel_name='res.partner',
                                         string='Invoice Address')

    _depends = {
        'account.move.line': [
            'account_id', 'company_id', 'credit', 'date', 'debit',
            'followup_date', 'followup_line_id', 'partner_id', 'reconcile_id',
        ],
        'account.account': ['internal_type', 'deprecated'],
    }


class AccountFollowupSendingResults(models.TransientModel):
    _name = 'account_followup.sending.results'
    _description = 'Results from the sending of the different letters and emails'

    @api.multi
    def do_report(self):
        self.ensure_one()
        return self._context.get('report_data')

    def _default_description(self):
        return self._context.get('description', '')

    def _default_needprinting(self):
        return self._context.get('needprinting', '')

    description = fields.Text(readonly=True,
                              default=lambda self:
                                  self._default_description())
    needprinting = fields.Boolean("Needs Printing",
                                  default=lambda self:
                                      self._default_needprinting())


class AccountFollowupPrint(models.TransientModel):
    _name = 'account_followup.print'
    _description = 'Print Follow-up & Send Mail to Customers'

    # Default methods
    @api.model
    def _default_followup(self):
        company_id = self._context.get('company_id',
                                       self.env.user.company_id.id)
        return self.env['account_followup.followup'].search([
            ('company_id', '=', company_id)])

    date = fields.Date(string='Follow-up Sending Date', required=True,
                       default=lambda *a: time.strftime('%Y-%m-%d'),
                       help="This field allow you to select a forecast date "
                            "to plan your follow-ups")
    followup_id = fields.Many2one('account_followup.followup', 'Follow-Up',
                                  default=lambda self:
                                      self._default_followup(),
                                  required=True, readonly=True)
    partner_ids = fields.Many2many('account_followup.stat.by.partner',
                                   'partner_stat_rel',
                                   'osv_memory_id', 'partner_id',
                                   string='Partners', required=True)
    company_id = fields.Many2one(related='followup_id.company_id',
                                 store=True, readonly=True)
    email_conf = fields.Boolean('Send Email Confirmation')
    email_subject = fields.Char(size=64, default="Invoices Reminder")
    partner_lang = fields.Boolean('Send Email in Partner Language',
                                  default=True,
                                  help="Do not change message text, if you "
                                       "want to send email in partner language"
                                       ", or configure from company")
    email_body = fields.Text(default=None)
    summary = fields.Text(readonly=True)
    test_print = fields.Boolean(help="Check if you want to print follow-ups "
                                     "without changing follow-up level.")

    @api.multi
    # TODO
    def do_process(self):
        self.ensure_one()
        import ipdb
        ipdb.set_trace()
        context = dict(self.env.context or {})

        # Get partners
        tmp = self._get_partners_followp()
        partner_list = tmp['partner_ids']
        to_update = tmp['to_update']

        # Update partners
        self.do_update_followup_level(to_update, partner_list)
        # process the partners (send mails...)
        restot_context = context.copy()
        restot = self.process_partners(
            cr, uid, partner_list, data, context=restot_context)
        context.update(restot_context)
        # clear the manual actions if nothing is due anymore
        nbactionscleared = self.clear_manual_actions(
            cr, uid, partner_list, context=context)
        if nbactionscleared > 0:
            restot['resulttext'] = restot['resulttext'] + "<li>" + \
                _("%s partners have no credits and as such the action is cleared") % (
                    str(nbactionscleared)) + "</li>"
        # return the next action
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), (
            'name', '=', 'view_account_followup_sending_results')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=[
                                   'res_id'], context=context)[0]['res_id']
        context.update(
            {'description': restot['resulttext'], 'needprinting': restot['needprinting'], 'report_data': restot['action']})
        return {
            'name': _('Send Letters and Emails: Actions Summary'),
            'view_type': 'form',
            'context': context,
            'view_mode': 'tree,form',
            'res_model': 'account_followup.sending.results',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _get_partners_followp(self):
        self.ensure_one()
        company_id = self.company_id.id
        context = self._context
        cr = self._cr
        cr.execute(
            "SELECT l.partner_id, l.followup_line_id,l.date_maturity, l.date, l.id "
            "FROM account_move_line AS l "
            "LEFT JOIN account_account AS a "
            "ON (l.account_id=a.id) "
            "WHERE (l.full_reconcile IS NULL) "
            "AND (a.type='receivable') "
            "AND (l.state<>'draft') "
            "AND (l.partner_id is NOT NULL) "
            "AND (not a.deprecated) "
            "AND (l.debit > 0) "
            "AND (l.company_id = %s) "
            "AND (l.blocked = False)"
            "ORDER BY l.date", (company_id,))  # l.blocked added to take litigation into account and it is not necessary to change follow-up level of account move lines without debit
        move_lines = cr.fetchall()
        old = None
        fups = {}
        fup_id = 'followup_id' in context and context['followup_id'] or self.followup_id.id
        date = 'date' in context and context['date'] or self.date

        current_date = fields.Date.context_today(self)
        cr.execute(
            "SELECT * "
            "FROM account_followup_followup_line "
            "WHERE followup_id=%s "
            "ORDER BY delay", (fup_id,))

        # Create dictionary of tuples where first element is the date to compare with the due date and second element is the id of the next level
        for result in cr.dictfetchall():
            delay = datetime.timedelta(days=result['delay'])
            fups[old] = (current_date - delay, result['id'])
            old = result['id']

        partner_list = []
        to_update = {}

        # Fill dictionary of accountmovelines to_update with the partners that need to be updated
        for partner_id, followup_line_id, date_maturity, date, id in move_lines:
            if not partner_id:
                continue
            if followup_line_id not in fups:
                continue
            stat_line_id = partner_id * 10000 + company_id
            if date_maturity:
                if date_maturity <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                    if stat_line_id not in partner_list:
                        partner_list.append(stat_line_id)
                    to_update[str(id)] = {
                        'level': fups[followup_line_id][1], 'partner_id': stat_line_id}
            elif date and date <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                if stat_line_id not in partner_list:
                    partner_list.append(stat_line_id)
                to_update[str(id)] = {
                    'level': fups[followup_line_id][1], 'partner_id': stat_line_id}
        return {'partner_ids': partner_list, 'to_update': to_update}
