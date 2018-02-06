# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# Copyright 2018 Access Bookings Ltd (https://accessbookings.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import Warning
from odoo import fields, models, api, _


class Followup(models.Model):
    """ Followup model base class """

    _name = 'account_followup.followup'
    _description = 'Account Follow-up'

    # Fields Declaration
    followup_line = fields.One2many('account_followup.followup.line',
                                    'followup_id',
                                    string='Followup',
                                    copy=True)
    company_id = fields.Many2one('res.company',
                                 required=True, string='Company',
                                 default=lambda self:
                                     self.env['res.company'].
                                     _company_default_get(
                                         'account_followup.followup'))
    name = fields.Char(related='company_id.name',
                       store=True, readonly=True)

    _sql_constraints = [('company_uniq', 'unique(company_id)',
                        'Only one follow-up per company is allowed')]


class FollowupLine(models.Model):
    """ Followup lines model """

    _name = 'account_followup.followup.line'
    _description = 'Follow-up Criteria'
    _order = 'delay'
    _default_mail_description = _("""
        Dear %(partner_name)s,

Exception made if there was a mistake of ours, it seems that the following
 amount stays unpaid. Please, take appropriate measures in order to carry out
 this payment in the next 8 days.

Would your payment have been carried out after this mail was sent, please
ignore this message. Do not hesitate to contact our accounting department.

Best Regards,
    """)

    # Fields Declaration
    name = fields.Char('Follow-Up Action', required=True)
    sequence = fields.Integer(help="Gives the sequence order when \
                                displaying a list of follow-up lines.")
    delay = fields.Integer('Due Days',
                           help="The number of days after the due date of the \
                           invoice to wait before sending the reminder.  \
                           Could be negative if you want to send a polite \
                           alert beforehand.",
                           required=True)
    followup_id = fields.Many2one('account_followup.followup',
                                  'Follow Ups',
                                  required=True,
                                  ondelete="cascade")
    description = fields.Text('Printed Message', translate=True,
                              default=_default_mail_description)
    send_email = fields.Boolean('Send an Email', default=True,
                                help="When processing, it will send an email")
    send_letter = fields.Boolean('Send a Letter', default=True,
                                 help="When processing, \
                                 it will print a letter")
    manual_action = fields.Boolean(default=False,
                                   help="When processing, it will set the \
                                    manual action to be taken for that \
                                    customer. ")
    manual_action_note = fields.Text('Action To Do',
                                     placeholder="e.g. Give a phone call, \
                                     check with others , ...")
    manual_action_responsible_id = fields.Many2one('res.users',
                                                   'Assign a Responsible',
                                                   ondelete='set null')
    email_template_id = fields.Many2one('mail.template',
                                        'Email Template',
                                        ondelete='set null')

    _sql_constraints = [('days_uniq', 'unique(followup_id, delay)',
                         'Days of the follow-up levels must be different')]

    # Constraints and onchanges
    @api.constrains('description')
    def _check_description(self):
        """ Check followup line description """
        for line in self:
            if line.description:
                try:
                    line.description % {'partner_name': '', 'date': '',
                                        'user_signature': '',
                                        'company_name': ''}
                except Exception as e:
                    raise Warning(_('Your description is invalid, \
                    use the right legend or %% if you want to use \
                    the percent character.'))


class AccountMoveLine(models.Model):
    """ ADD followup line and date """

    _inherit = 'account.move.line'

    # Fields Declaration
    followup_line_id = fields.Many2one('account_followup.followup.line',
                                       'Follow-up Level',
                                       # restrict deletion of the followup line
                                       ondelete='restrict')
    followup_date = fields.Date('Latest Follow-up', index=1)
    # 'balance' field is not the same
    result = fields.Float(compute="_compute_result", string="Balance")

    # compute fields
    @api.multi
    @api.depends('debit', 'credit')
    def _compute_result(self):
        """ Compute result field
        result = debit - credit
        """
        for aml in self:
            aml.result = aml.debit - aml.credit


class ResPartner(models.Model):
    """ Add followup fields on partner model """

    _inherit = 'res.partner'

    # Fields Declaration
    payment_responsible_id = fields.Many2one(
        'res.users', ondelete='set null', string='Follow-up Responsible',
        help="Optionally you can assign a user to this field, which "
             "will make him responsible for the action.",
        track_visibility="onchange", copy=False)
    payment_note = fields.Text(
        'Customer Payment Promise',
        help="Payment Note", track_visibility="onchange", copy=False)
    payment_next_action = fields.Text(
        'Next Action', copy=False,
        help="This is the next action to be taken. It will automatically be "
             "set when the partner gets a follow-up level that "
             "requires a manual action. ", track_visibility="onchange")
    payment_next_action_date = fields.Date(
        'Next Action Date',
        copy=False, help="This is when the manual follow-up is needed. The \
        date will be set to the current date when the partner gets a \
        follow-up level that requires a manual action. Can be practical to \
        set manually e.g. to see if he keeps his promises.")
    unreconciled_aml_ids = fields.One2many(
        'account.move.line', 'partner_id',
        auto_join=True,
        domain=['&', ('full_reconcile_id', '=', False), '&',
                ('account_id.deprecated', '!=', True), '&',
                ('account_id.internal_type', '=', 'receivable'),
                ('invoice_id', '!=', False),
                ('move_id.state', '!=', 'draft')])
    latest_followup_date = fields.Date(
        compute="_compute_latest_followup_date",
        string="Latest Follow-up Date", help="Latest date that the follow-up \
        level of the partner was changed")
    latest_followup_level_id = fields.Many2one(
        'account_followup.followup.line',
        compute="_compute_latest_followup_date", store=True,
        string="Latest Follow-up Level", help="The maximum follow-up level")
    latest_followup_level_id_without_lit = fields.Many2one(
        'account_followup.followup.line',
        compute="_compute_latest_followup_date", store=True,
        string="Latest Follow-up Level without litigation",
        help="The maximum follow-up level without taking into account \
         the account move lines with litigation")
    payment_amount_due = fields.Float(
        compute="_compute_amounts_and_date", string="Amount Due",
        search="_search_payment_amount_due"
        )
    payment_amount_overdue = fields.Float(
        compute="_compute_amounts_and_date",
        string="Amount Overdue",
        search="_search_payment_amount_overdue"
        )
    payment_earliest_due_date = fields.Date(
        compute="_compute_amounts_and_date",
        string="Worst Due Date",
        # TODO Implement search functionality
        # search="_payment_earliest_date_search"
        )

    # Compute methods
    @api.multi
    @api.depends('unreconciled_aml_ids.followup_line_id',
                 'unreconciled_aml_ids.partner_id')
    def _compute_latest_followup_date(self):
        """ Get latest followup date """
        company = self.env.user.company_id
        for partner in self:
            latest_date = False
            latest_level = False
            latest_days = False
            latest_level_without_lit = False
            latest_days_without_lit = False
            for aml in partner.unreconciled_aml_ids:
                if (aml.company_id == company) and \
                   (aml.followup_line_id) and \
                   (not latest_days or
                        latest_days < aml.followup_line_id.delay):
                    latest_days = aml.followup_line_id.delay
                    latest_level = aml.followup_line_id.id
                if (aml.company_id == company) and \
                   (not latest_date or latest_date < aml.followup_date):
                    latest_date = aml.followup_date
                if (aml.company_id == company) and \
                   (aml.blocked is False) and \
                   (aml.followup_line_id and
                    (not latest_days_without_lit or
                     (latest_days_without_lit < aml.followup_line_id.delay)
                     )):
                    latest_days_without_lit = aml.followup_line_id.delay
                    latest_level_without_lit = aml.followup_line_id.id
            partner.latest_followup_date = latest_date
            partner.latest_followup_level_id = latest_level
            partner.latest_followup_level_id_without_lit = \
                latest_level_without_lit

    # TODO depends field missing
    @api.multi
    @api.depends()
    def _compute_amounts_and_date(self):
        """
        Function that computes values for the followup functional fields.
        Note that 'payment_amount_due' is similar to 'credit' field on
        res.partner except it filters on user's company.
        """
        company = self.env.user.company_id
        current_date = fields.Date.context_today(self)
        for partner in self:
            worst_due_date = False
            amount_due = amount_overdue = 0.0
            for aml in partner.unreconciled_aml_ids:
                if (aml.company_id == company):
                    date_maturity = aml.date_maturity or aml.date
                    if not worst_due_date or date_maturity < worst_due_date:
                        worst_due_date = date_maturity
                    amount_due += aml.result
                    if (date_maturity <= current_date):
                        amount_overdue += aml.result
            partner.payment_amount_due = amount_due
            partner.payment_amount_overdue = amount_overdue
            partner.payment_earliest_due_date = worst_due_date

    # Search methods
    def _search_payment_amount_due(self, operator, value):
        query, qargs = self._get_followup_overdue_query(operator, value)
        self._cr.execute(query, qargs)
        res = self._cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]

    def _search_payment_amount_overdue(self, operator, value):
        return self.with_context(overdue=True).\
            _search_payment_amount_due(operator, value)

    # Actions methods
    @api.multi
    def action_button_print(self):
        """ Print Overdue Payments button action """
        self.ensure_one()
        company_id = self.env.user.company_id.id
        aml = self.env['account.move.line'].search([
                ('partner_id', '=', self.id),
                ('account_id.internal_type', '=', 'receivable'),
                ('full_reconcile_id', '=', False),
                ('company_id', '=', company_id),
                '|', ('date_maturity', '=', False),
                ('date_maturity', '<=', fields.Date.context_today(self))])
        if not aml:
            raise Warning(_('Error!'), _("The partner does not have any "
                                         "accounting entries to print in the "
                                         "overdue report for the current "
                                         "company."))
        followup = self.env['account_followup.followup'].\
            search([('company_id', '=', company_id)])
        if not followup:
            raise Warning(_('Error!'),
                          _("There is no followup plan defined for "
                            "the current company."))
        self.message_post(body=_('Printed overdue payments report'))
        return self.env.ref('account.action_report_print_overdue').\
            report_action(self)

    @api.multi
    def action_partner_mail(self):
        self.ensure_one()
        for partner in self:
            partners_to_email = partner.child_ids.filtered(
                                lambda r: r.type == 'invoice' and
                                r.email)
            if not partners_to_email and partner.email:
                partners_to_email = partner
            if partners_to_email:
                level = partner.latest_followup_level_id_without_lit
                for partner_to_email in partners_to_email:
                    if level and level.send_email \
                             and level.email_template_id \
                             and level.email_template_id.id:
                        level.email_template_id.send_mail(partner_to_email.id)
                    else:
                        mail_template = self.env.ref(
                            "account_followup."
                            "email_template_account_followup_default")
                        mail_template.send_mail(partner_to_email.id)

    # Busniess methods
    def _get_followup_overdue_query(self, operator, value):
        """
            Get followup query
        """
        overdue = self._context.get('overdue', False)
        company_id = self.env.user.company_id.id
        having_where_clause = ' (SUM(bal2) %s %s)' % (operator, value)
        overdue_only_str = overdue and 'AND date_maturity <= NOW()' or ''
        return ('''SELECT pid AS partner_id, SUM(bal2) FROM
                    (SELECT CASE WHEN bal IS NOT NULL THEN bal
                    ELSE 0.0 END AS bal2, p.id as pid FROM
                    (SELECT (debit-credit) AS bal, partner_id
                    FROM account_move_line l
                    WHERE account_id IN
                            (SELECT id FROM account_account
                            WHERE internal_type=\'receivable\' AND
                             not deprecated)
                    ''' + overdue_only_str + '''
                    AND full_reconcile_id IS NULL
                    AND company_id = %s ) AS l
                    RIGHT JOIN res_partner p
                    ON p.id = partner_id ) AS pl
                    GROUP BY pid HAVING ''' + having_where_clause,
                [company_id])
