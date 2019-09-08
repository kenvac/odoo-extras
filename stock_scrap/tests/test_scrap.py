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

    def test_scrap_1(self):
        """ Check the Stcok scrap cost and total cost field.
        """

        scrap = self.env['stock.scrap'].create({
            'product_id': self.product1.id,
            'product_uom_id': self.product1.uom_id.id,
            'scrap_qty': 1,
        })

        # onchange product_id
        scrap._onchange_product_id()
        self.assertEqual(scrap.cost, 7.0)
        self.assertEqual(scrap.total_cost, 7.0)

        # onchange scrap_qty
        scrap.scrap_qty = 2
        scrap._onchange_cost()
        self.assertEqual(scrap.total_cost, 14.0)
        self.assertEqual(scrap.cost, 7.0)
        self.assertEqual(scrap.scrap_qty, 2)

        # onchange cost
        scrap.cost = 20
        scrap._onchange_cost()
        self.assertEqual(scrap.total_cost, 40.0)
        self.assertEqual(scrap.cost, 20.0)
        self.assertEqual(scrap.scrap_qty, 2)

        # onchange product_id
        scrap.product_id = self.product2.id
        scrap._onchange_product_id()
        # Qty = 2, total = 2 * 10 (cost price of product 2)
        self.assertEqual(scrap.total_cost, 20.0)
        self.assertEqual(scrap.cost, 10.0)
        self.assertEqual(scrap.scrap_qty, 2)

        # _compute_total_cost
        scrap.scrap_qty = 1
        scrap._onchange_cost()
        scrap.do_scrap()
        self.assertEqual(scrap.total_cost, 10.0)
        self.assertEqual(scrap.cost, 10.0)
        self.assertEqual(scrap.scrap_qty, 1)

        self.assertEqual(scrap.state, 'done')
        move = scrap.move_id
        self.assertEqual(move.state, 'done')
        self.assertEqual(move.product_uom_qty, 1)
        self.assertEqual(move.scrapped, True)
        self.assertEqual(self.product1.qty_available, 0.0)
