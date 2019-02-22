# -*- coding: utf-8 -*-
# Copyright 2019 Kinner Vachhani>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Product Where Used Report',
    'version': '8.0.1.0.0',
    'summary': 'Search product on SO, PO, BOM and MO',
    'category': 'Stock',
    'author': 'Kinner Vachhani, Odoo Community Association (OCA)',
    'website': 'https://github.com/kenvac/odoo-extras',
    'license': 'AGPL-3',
    'depends': [
        'purchase',
        'sale',
        'mrp',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard_where_used_report_view.xml',
        'reports/where_used_report_xlsx.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
