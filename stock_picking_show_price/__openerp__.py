# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Show Price in Picking Lines",
    "summary": "Show Price in Picking Lines",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "security/picking_price_security.xml",
        "views/stock_view.xml",
    ],

}
