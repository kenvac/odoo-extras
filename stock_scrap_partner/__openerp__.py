# -*- coding: utf-8 -*-
# Copyright 2018 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Scrap Partner",
    "summary": "Adds Partner to stock_scrap module",
    "version": "8.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_scrap_reason",
    ],
    "data": [
        "views/stock_scrap_reason_view.xml",
        "views/stock_scrap_views.xml",
    ],
}
