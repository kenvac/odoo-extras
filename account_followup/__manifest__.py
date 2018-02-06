# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
# Copyright 2018 Access Bookings Ltd (https://accessbookings.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Payment Follow-up Management",
    "version": "11.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://accessbookings.com",
    "author": "Kinner Vachhani (Access Bookings), \
                Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'account', 'mail'
    ],
    "data": [
        "security/account_followup_security.xml",
        "security/ir.model.access.csv",
        "data/account_followup.xml",
        "views/account_followup_customers.xml",
        "wizard/account_followup_print.xml",
        "report/account_followup_report.xml",

    ],
    "demo": [
        "demo/account_followup.xml"
    ],
    "qweb": [
    ]
}
