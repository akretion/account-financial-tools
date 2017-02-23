# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#    This module copyright (C) 2013 Camptocamp (<http://www.camptocamp.com>).
#    This module copyright (C) 2013 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    #TODO test me
    def product_id_change(self, cr, uid, *args, **kwargs):
        tax_obj = self.pool['account.tax']
        res = super(sale_order_line, self).product_id_change(cr, uid, *args, **kwargs)

        #Depending of the order of the onchange the key can be in the args or in the kwargs
        if 'date_order' in kwargs:
            date_order = kwargs['date_order']
        else:
            date_order = args[11]

        tax_ids = []
        
        if date_order:
            original_tax_ids = res.get('value', {}).get('tax_id', [])

            for tax in tax_obj.browse(cr, uid, original_tax_ids, context=context):
                if not tax_obj._check_tax_validity(cr, uid, tax, date_order, context=context):
                    new_tax_id = tax_obj._map_tax(cr, uid, tax, date_order, context=context)
                    tax_ids.append(new_tax_id)
                else:
                    tax_ids.append(tax.id)
            res['tax_id'] = tax_ids
        return res


