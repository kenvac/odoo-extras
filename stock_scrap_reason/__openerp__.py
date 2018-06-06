# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Scrap Reason",
    "summary": "Adds scrap reason to stock_scrap module",
    "version": "8.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "stock_scrap",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_scrap_views.xml",
        "views/mrp_view.xml",
        "views/stock_view.xml",
    ],
}
