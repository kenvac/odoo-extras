# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.tools import float_compare


class StockScrap(models.Model):
    _name = 'stock.scrap'
    _order = 'id desc'

    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search([
            ('scrap_location', '=', True),
            ('company_id', 'in', [self.env.user.company_id.id, False])
            ], limit=1).id

    def _get_default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

    @api.depends('cost', 'scrap_qty')
    def _compute_total_cost(self):
        self.total_cost = (self.scrap_qty or 0.0) * self.cost

    name = fields.Char(
        'Reference', default=lambda self: _('New'),
        copy=False, readonly=True, required=True,
        states={'done': [('readonly', True)]})
    origin = fields.Char(string='Source Document')
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True, states={'done': [('readonly', True)]})
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        required=True, states={'done': [('readonly', True)]})
    # tracking = fields.Selection('Product Tracking', readonly=True,
    # related="product_id.tracking")
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot',
        states={'done': [('readonly', True)]},
        domain="[('product_id', '=', product_id)]")
    package_id = fields.Many2one(
        'stock.quant.package', 'Package',
        states={'done': [('readonly', True)]})
    owner_id = fields.Many2one('res.partner', 'Owner',
                               states={'done': [('readonly', True)]})
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Picking',
                                 states={'done': [('readonly', True)]})
    location_id = fields.Many2one(
        'stock.location', 'Location', domain="[('usage', '=', 'internal')]",
        required=True, states={'done': [('readonly', True)]},
        default=lambda self: self._get_default_location_id())
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location',
        default=lambda self: self._get_default_scrap_location_id(),
        domain="[('scrap_location', '=', True)]",
        required=True, states={'done': [('readonly', True)]})
    scrap_qty = fields.Float('Quantity', default=1.0,
                             required=True,
                             states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], string='Status', default="draft")
    date_expected = fields.Datetime('Expected Date',
                                    default=fields.Datetime.now)
    cost = fields.Float('Unit Cost Price', default=0.0,
                        help="Cost Price per unit")
    total_cost = fields.Float(help="""Total Scap Total. Total """
                                   """Scrap quantity * Unit Cost price""",
                              compute=lambda self: self._compute_total_cost())

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.total_cost = self.cost = 0.0
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.cost = self.product_id.standard_price
            self.total_cost = self.scrap_qty * self.cost

    @api.onchange('scrap_qty')
    def _onchange_scrap_qty(self):
        uom = self.env['product.uom']
        if self.product_id:
            uom_qty = uom._compute_qty(self.product_uom_id.id, self.scrap_qty,
                                       self.product_id.uom_id.id)
            self.total_cost = uom_qty * self.cost

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if self.picking_id:
            self.location_id = (self.picking_id.state == 'done') and \
                self.picking_id.location_dest_id.id \
                or self.picking_id.location_id.id

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.scrap') or _('New')
        scrap = super(StockScrap, self).create(vals)
        return scrap

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise ValidationError(_(
                'You cannot delete a scrap which is done.'))
        return super(StockScrap, self).unlink()

    def _get_origin_moves(self):
        return self.picking_id and self.picking_id.move_lines.filtered(
            lambda x: x.product_id == self.product_id)

    def _prepare_move_values(self):
        self.ensure_one()
        return {
            'name': self.name,
            'origin': self.origin or self.picking_id.name or self.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.scrap_qty,
            'location_id': self.location_id.id,
            'scrapped': True,
            'location_dest_id': self.scrap_location_id.id,
            'picking_id': self.picking_id.id
        }

    @api.multi
    def do_scrap(self):
        for scrap in self:
            move = self.env['stock.move'].create(scrap._prepare_move_values())
            move.action_done()
            scrap.write({'move_id': move.id, 'state': 'done'})
        return True

    @api.multi
    def action_get_stock_move_lines(self):
        action = self.env.ref('stock.action_move_form2').read([])[0]
        action['domain'] = [('id', '=', self.move_id.id)]
        return action

    @api.multi
    def action_validate(self):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        available_qty = sum(self.env['stock.quant']._gather(
            self.product_id,
            self.location_id,
            self.lot_id,
            self.package_id,
            self.owner_id,
            strict=True).mapped('qty'))
        if float_compare(available_qty,
                         self.scrap_qty,
                         precision_digits=precision) >= 0:
            return self.do_scrap()
        else:
            return {
                'name': _('Insufficient Quantity'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.scrap',
                'view_id': self.env.ref(
                    'stock_scrap.'
                    'stock_warn_insufficient_qty_scrap_form_view').id,
                'type': 'ir.actions.act_window',
                'context': {
                    'default_product_id': self.product_id.id,
                    'default_location_id': self.location_id.id,
                    'default_scrap_id': self.id
                },
                'target': 'new'
                }
