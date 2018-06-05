.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=============================================
Stock Valuation report on last purchase price
=============================================

This module generates xlsx valuation report based on last
purchase price or standard price.

E.g

Product A
    Last purchase price = £2
    Standard price = £4
    Stock in hand = 10

Product B
    Last purchase price = £3
    Standard price = £5
    Stock in hand = 10

Product C (Spare parts never purchased)
    Standard price = £0.01
    Stock in hand = 100

Valuation report
    Product A = £2 * 10 (Stock in hand)  = £20
    Product B = £3 * 10 (Stock in hand)  = £30
    Product c = £0.01 * 100 (Stock in hand)  = £1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/kenvac/odoo-extras/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Contributors
============

* Kinner Vachhani <kin.vachhani@gmail.com>

Do not contact contributors directly about support or help with technical issues.
