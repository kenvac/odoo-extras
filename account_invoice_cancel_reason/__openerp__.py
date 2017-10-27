# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Invoice Cancel Reason",
    "summary": "Invoice Cancel Reason",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_cancel",
    ],
    "data": [
        'security/ir.model.access.csv',
        "data/data_invoice_cancel_reason.xml",
        "views/account_invoice_cancel_reason_view.xml",
        "wizard/wizard_invoice_cancel_reason_view.xml",
        "views/account_invoice_view.xml"
    ],

}
