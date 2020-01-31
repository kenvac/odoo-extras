# Copyright 2020 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Scrap Reason",
    "summary": "Adds scrap reason option when scrapping product",
    "version": "12.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Kinner Vachhani, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "data/stock.scrap.reason.csv",
        "security/ir.model.access.csv",
        "views/stock_scrap_views.xml",
        "views/stock_scrap_reason.xml",
        "views/stock_view.xml",
    ],
}
