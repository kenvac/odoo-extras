# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Valuation Report last purchase price",
    "summary": "Generate Stock Valuation Report based on last purchase price",
    "version": "8.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "mrp",
        "report_xlsx",
    ],
    "data": [
        "views/stock_valuation_report_view.xml",

    ],

}
