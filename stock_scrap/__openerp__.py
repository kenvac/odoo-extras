# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Scrap Stock",
    "summary": "Back of stock scrap functionality from V11",
    "version": "8.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "data/stock_data.xml",
        "security/ir.model.access.csv",
        "views/stock_scrap_views.xml",
        "wizard/stock_warn_insufficient_qty_view.xml",
    ],
}
