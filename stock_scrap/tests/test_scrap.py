# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase


class StockMove(TransactionCase):
    def setUp(self):
        super(StockMove, self).setUp()
        self.InvObj = self.env['stock.inventory']
        self.InvLineObj = self.env['stock.inventory.line']
        self.StockQuantObj = self.env['stock.quant']
        self.stock_location = self.env.ref(
            'stock.stock_location_stock')
        self.customer_location = self.env.ref(
            'stock.stock_location_customers')
        self.supplier_location = self.env.ref(
            'stock.stock_location_suppliers')
        self.product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': self.env.ref(
                'product.product_category_all').id,
        })
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_dozen = self.env.ref('product.product_uom_dozen')
        self.product2 = self.env['product.product'].create({
            'name': 'Product 2',
            'type': 'consu',
            'categ_id': self.env.ref(
                'product.product_category_all').id,
        })

    def test_scrap_1(self):
        """ Check the created stock move and
        the impact on quants when we scrap a
        stockable product.
        """

        inventory = self.InvObj.create({'name': 'Test',
                                        'product_id': self.product1.id,
                                        'filter': 'product'})
        inventory.prepare_inventory()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.InvLineObj.create({
            'inventory_id': inventory.id,
            'product_id': self.product1.id,
            'product_qty': 1,
            'location_id': self.stock_location.id})
        inventory.action_done()
        # Check quantity available of product 1.
        quants = self.StockQuantObj.search([('product_id', '=',
                                             self.product1.id),
                                            ('location_id', '=',
                                             self.stock_location.id)])
        total_qty = [quant.qty for quant in quants]
        self.assertEqual(sum(total_qty), 1,
                         'Expecting 1 Units , got %.4f '
                         'Units on location stock!'
                         % (sum(total_qty)))
        self.assertEqual(self.product1.qty_available,
                         1,
                         'Expecting 1 Units , got %.4f Units'
                         ' of quantity available!'
                         % (self.product1.qty_available))

        scrap = self.env['stock.scrap'].create({
            'product_id': self.product1.id,
            'product_uom_id': self.product1.uom_id.id,
            'scrap_qty': 1,
        })
        scrap.do_scrap()
        self.assertEqual(scrap.state, 'done')
        move = scrap.move_id
        self.assertEqual(move.state, 'done')
        self.assertEqual(move.product_uom_qty, 1)
        self.assertEqual(move.scrapped, True)
        self.assertEqual(self.product1.qty_available, 0.0)

    def test_scrap_2(self):
        """ Check the created stock move and the impact on quants
        when we scrap a consumable product.
        """
        scrap = self.env['stock.scrap'].create({
            'product_id': self.product2.id,
            'product_uom_id': self.product2.uom_id.id,
            'scrap_qty': 1,
        })
        scrap.do_scrap()
        self.assertEqual(scrap.state, 'done')
        move = scrap.move_id
        self.assertEqual(move.state, 'done')
        self.assertEqual(move.product_uom_qty, 1)
        self.assertEqual(move.scrapped, True)
        self.assertEqual(self.product1.qty_available, 0.0)

    def test_scrap_3(self):
        """ Scrap the product of a reserved move line.
        Check that the move line is correctly deleted and
        that the associated stock move is not assigned anymore.
        """
        inventory = self.InvObj.create({'name': 'Test',
                                        'product_id': self.product1.id,
                                        'filter': 'product'})
        inventory.prepare_inventory()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.InvLineObj.create({
            'inventory_id': inventory.id,
            'product_id': self.product1.id,
            'product_qty': 1,
            'location_id': self.stock_location.id})
        inventory.action_done()

        move1 = self.env['stock.move'].create({
            'name': 'test_scrap_3',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
        })
        move1.action_confirm()
        move1.action_assign()
        self.assertEqual(move1.state, 'assigned')

        scrap = self.env['stock.scrap'].create({
            'product_id': self.product1.id,
            'product_uom_id': self.product1.uom_id.id,
            'scrap_qty': 1,
        })
        scrap.do_scrap()
        self.assertEqual(move1.state, 'confirmed')

    def test_scrap_4(self):
        """ Scrap the product of a picking. Then modify the
        done linked stock move and ensure the scrap quantity is also
        updated.
        """
        inventory = self.InvObj.create({'name': 'Test',
                                        'product_id': self.product1.id,
                                        'filter': 'product'})
        inventory.prepare_inventory()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.InvLineObj.create({
            'inventory_id': inventory.id,
            'product_id': self.product1.id,
            'product_qty': 10,
            'location_id': self.stock_location.id})
        inventory.action_done()

        partner = self.env['res.partner'].create({'name': 'Kimberley'})
        picking = self.env['stock.picking'].create({
            'name': 'A single picking with one move to scrap',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'partner_id': partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        })
        move1 = self.env['stock.move'].create({
            'name': 'A move to confirm and scrap its product',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_id': picking.id,
        })
        move1.action_confirm()

        self.assertEqual(move1.state, 'confirmed')
        scrap = self.env['stock.scrap'].create({
            'product_id': self.product1.id,
            'product_uom_id': self.product1.uom_id.id,
            'scrap_qty': 5,
            'picking_id': picking.id,
        })

        scrap.action_validate()
        self.assertEqual(len(picking.move_lines), 2)
        scrapped_move = picking.move_lines.filtered(
            lambda m: m.state == 'done')
        self.assertTrue(scrapped_move, 'No scrapped move created.')
        self.assertEqual(scrapped_move.scrap_ids.ids,
                         [scrap.id],
                         'Wrong scrap linked to the move.')
        self.assertEqual(scrap.scrap_qty, 5,
                         'Scrap quantity has been modified and is not '
                         'correct anymore.')

    def test_scrap_5(self):
        """ Scrap the product of a reserved move line where
        the product is reserved in another unit of measure.
        Check that the move line is correctly updated after the scrap.
        """
        # 4 units are available in stock
        inventory = self.InvObj.create({'name': 'Test',
                                        'product_id': self.product1.id,
                                        'filter': 'product'})
        inventory.prepare_inventory()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.InvLineObj.create({
            'inventory_id': inventory.id,
            'product_id': self.product1.id,
            'product_qty': 16,
            'location_id': self.stock_location.id})
        inventory.action_done()

        # scrap a unit
        scrap = self.env['stock.scrap'].create({
            'product_id': self.product1.id,
            'product_uom_id': self.uom_dozen.id,
            'scrap_qty': 1,
            # 'picking_id': picking.id,
        })
        scrap.action_validate()
        self.assertEqual(scrap.state, 'done')
        self.assertEqual(self.product1.qty_available, 4)
