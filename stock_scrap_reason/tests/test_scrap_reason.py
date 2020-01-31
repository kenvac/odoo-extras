# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class StockMove(TransactionCase):
    def setUp(self):
        super(StockMove, self).setUp()

        self.product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'standard_price': 7.0,
            'categ_id': self.env.ref(
                'product.product_category_all').id,
        })

        self.product2 = self.env['product.product'].create({
            'name': 'Product 2',
            'type': 'consu',
            'standard_price': 10.0,
            'categ_id': self.env.ref(
                'product.product_category_all').id,
        })

    def test_scrap_reason_1(self):
        """ Check Manual Stock scrap reason.
        """

        scrap = self.env['stock.scrap'].create({
            'product_id': self.product1.id,
            'product_uom_id': self.product1.uom_id.id,
            'scrap_qty': 1,
            'reason_id': self.env.ref(
                'stock_scrap_reason.scrap_reason_5').id,
        })

        scrap.do_scrap()
        self.assertEqual(scrap.reason_id.name, 'R&D')
