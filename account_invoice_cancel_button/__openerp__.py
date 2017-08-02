# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Hide Invoice Cancel Button",
    "summary": "Hide cancel button on invoice",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "author": "Kinner Vachhani",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_cancel",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],

}
