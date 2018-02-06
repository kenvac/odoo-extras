# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# Copyright 2018 Access Bookings Ltd (https://accessbookings.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agp
from odoo import fields, models
from odoo import tools


class AccountFollowupStat(models.Model):
    _name = "account_followup.stat"
    _description = "Follow-up Statistics"
    _rec_name = 'partner_id'
    _auto = False
    _order = 'date_move'

    partner_id = fields.Many2one('res.partner', readonly=True)
    date_move = fields.Date('First move', readonly=True)
    date_move_last = fields.Date('Last move', readonly=True)
    date_followup = fields.Date('Latest followup', readonly=True)
    followup_id = fields.Many2one('account_followup.followup.line',
                                  'Follow Ups', readonly=True,
                                  ondelete="cascade")
    balance = fields.Float(readonly=True)
    debit = fields.Float(readonly=True)
    credit = fields.Float(readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    blocked = fields.Boolean(readonly=True)

    def init(self):
        cr = self.env.cr
        tools.drop_view_if_exists(cr, 'account_followup_stat')
        cr.execute("""
            create or replace view account_followup_stat as (
                SELECT
                    l.id as id,
                    l.partner_id AS partner_id,
                    min(l.date) AS date_move,
                    max(l.date) AS date_move_last,
                    max(l.followup_date) AS date_followup,
                    max(l.followup_line_id) AS followup_id,
                    sum(l.debit) AS debit,
                    sum(l.credit) AS credit,
                    sum(l.debit - l.credit) AS balance,
                    l.company_id AS company_id,
                    l.blocked as blocked
                FROM
                    account_move_line l
                    LEFT JOIN account_account a ON (l.account_id = a.id)
                WHERE
                    a.deprecated IS NOT False AND
                    a.internal_type = 'receivable' AND
                    l.full_reconcile_id is NULL AND
                    l.partner_id IS NOT NULL
                GROUP BY
                    l.id, l.partner_id, l.company_id, l.blocked
            )""")
