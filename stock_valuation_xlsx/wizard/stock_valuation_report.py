# -*- coding: utf-8 -*-
# Copyright 2017 Kinner Vachhani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
from openerp import tools


class WizardStockValuation(models.TransientModel):
    _name = "stock.valuation.report.xlsx"
    _description = "Stock Valuation Report"

    report_date = fields.Date()
    # _auto = False
    # product_id = fields.Many2one('product.product', 'Product')
    # unit_price = fields.Float("Price")
    # quantity = fields.Float("Quantity")
    # valuation = fields.Float("Valuation",
    #                          help="Valuation = Unit price * Quantity")

    def _get_product_last_pur_price(self):
        # drop_view_if_exists(self.cr, 'stock_valuation_report')
        cr = self._cr
        sql = """
              SELECT
                    MIN(template.id) as id,
                    template.id,
                    t.cost AS unit_price,
                    SUM(t.qty) AS quantity,
                    SUM(t.qty * t.cost) AS valuation  FROM (
                WITH quant AS
                (SELECT product_id, in_date, cost, id, location_id, qty,
                        ROW_NUMBER()
                    OVER (PARTITION BY product_id ORDER BY in_date DESC)
                    AS rownum
                    FROM stock_quant
                )
                SELECT q.product_id,
                    q.in_date,
                    q.cost,
                    q.id,
                    q.location_id,
                    q.qty
                FROM quant AS q WHERE rownum = 1
                ) AS t
                LEFT JOIN  product_product product ON
                        (product.id = t.product_id)
                LEFT JOIN product_template template ON
                    (template.id = product.product_tmpl_id)
                LEFT JOIN mrp_bom bom ON
                    (template.id = bom.product_tmpl_id
                        AND bom.product_id = product.id)
                LEFT JOIN stock_location loc ON (loc.id = t.location_id)
                WHERE
                    loc.usage = 'internal' AND loc.active IS TRUE
                GROUP BY template.id, t.cost
                ORDER BY template.id
        """
        cr.execute(sql)
        return cr.dictfetchall()

    def _get_allbom(self):
        sql = """
            SELECT id, product_tmpl_id from mrp_bom
        """
        cr = self._cr
        cr.execute(sql)
        return cr.fetchall()

    def _get_prodnot_bom(self):
        sql = """
              SELECT id FROM product_product prod
                WHERE prod.product_tmpl_id NOT IN (SELECT product_tmpl_id
                    FROM mrp_bom)
        """
        cr = self._cr
        cr.execute(sql)
        cr.execute(sql)
        return cr.fetchall()

    def bomCost(self):
        bom = self.env['mrp.bom']
        product = self.env['product.product']

        def getCost(bom, costDict):
            cost = 0.0
            for line in bom.bom_line_ids:
                if line.product_id.id in bomdict:
                    cost += getCost(bom.browse(line.product_id.id))
                    continue
                price = line.product_id.id in costDict \
                    and costDict[line.product_id.id]['unit_price'] \
                    or line.product_id.standard_price
                cost += price * line.product_qty
            return cost

        productsValuation = self._get_product_last_pur_price()
        valuationDict = dict((i['id'], i) for i in productsValuation)

        productZeroPriceDict = [i for i in productsValuation
                                if i['unit_price'] == 0.0]
        productZeroPriceList = [i['id'] for i in productZeroPriceDict]
        products = product.browse(productZeroPriceList).\
            filtered(lambda r: r.standard_price != 0.0)
        # Update product price dict with standard price if zero
        for product in products:
            valuationDict[product.id]['unit_price'] = \
                product.standard_price
        allBom = self._get_allbom()
        bomdict = dict((id, prod) for id, prod in allBom)
        xlsList = []
        for bom in bom.browse(bomdict.keys()):
            cost = getCost(bom, valuationDict)
            xlsList.append({'name': bom.product_tmpl_id.name,
                            'code': bom.product_tmpl_id.default_code,
                            'cost': cost,
                            'qty': bom.product_tmpl_id.qty_available,
                            'valuation':
                                cost*bom.product_tmpl_id.qty_available,
                            })
        product_ids = tools.flatten(self._get_prodnot_bom())
        for product in product.browse(product_ids):
            cost = product.id in valuationDict and \
                valuationDict[product.id]['unit_price'] or \
                product.standard_price
            row = {'name': product.name,
                   'code': product.default_code,
                   'cost': cost,
                   'qty': product.qty_available,
                   'valuation': cost * product.qty_available,
                   }
            xlsList.append(row)
        return xlsList

    @api.multi
    def create_report(self):
        self.ensure_one()
        data = self.bomCost()
        datas = {'form': data}
        return {'type': 'ir.actions.report.xml',
                'report_name': 'stock.valuation.xlsx',
                'datas': datas}
