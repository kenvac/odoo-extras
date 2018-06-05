# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp import models
from openerp.osv import expression


class StockQant(models.Model):
    _inherit = 'stock.quant'

    def _gather(self, product_id, location_id, lot_id=None, package_id=None,
                owner_id=None, strict=False):
        domain = [
            ('product_id', '=', product_id.id),
        ]
        if not strict:
            if lot_id:
                domain = expression.AND([[('lot_id', '=', lot_id.id)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)],
                                        domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)],
                                         domain])
            domain = expression.AND([[('location_id',
                                       'child_of',
                                       location_id.id)], domain])
        else:
            domain = expression.AND([[('lot_id', '=', lot_id and lot_id.id or
                                    False)], domain])
            domain = expression.AND([[('package_id', '=', package_id and
                                    package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and
                                    owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)],
                                    domain])

        return self.search(domain)
