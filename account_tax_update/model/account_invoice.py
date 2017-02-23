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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from lxml import etree
import logging


_logger = logging.getLogger(__name__)

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def invoice_validate(self, cr, uid, ids, context=None):
        config_obj = self.pool.get('account.update.tax.config')
        #To avoid lost of performance the test is only apply
        #when a config is in the confirm state
        if config_obj.exist_confirm_config(cr, uid):
            if config_obj.automatic_tax_update(cr, uid):
                self.update_invoice_tax(cr, uid, ids,
                    context=context,
                    automatic_update=True)

        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        #Check on tax is done after calling super because the date
        #can be empty
        if config_obj.exist_confirm_config(cr, uid):
            tax_obj = self.pool['account.tax']
            for invoice in self.browse(cr, uid, ids, context=None):
                for line in invoice.invoice_line:
                    for tax in line.invoice_line_tax_id:
                        tax_obj._check_tax_validity(cr, uid, tax,
                            invoice.date_invoice,
                            raise_exception=True,
                            context=context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(account_invoice, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            config_obj = self.pool.get('account.update.tax.config')
            if config_obj.exist_confirm_config(cr, uid):
                eview = etree.fromstring(result['arch'])
                header = eview.xpath("//header")[0]
                element = etree.Element('button', name='update_invoice_tax', string='Update Invoice Tax', type='object')
                header.insert(-1, element)
                result['arch'] = etree.tostring(eview, pretty_print=True)
        return result

    def update_invoice_tax(self, cr, uid, ids, context=None, automatic_update=False):
        tax_obj = self.pool['account.tax']
        for invoice in self.browse(cr, uid, ids, context=None):
            #If the date is empty we use the tody date. If the final date used
            #on the invoice is different, there is no big deal as the check on
            #tax will fail
            if not invoice.date_invoice:
                _logger.debug('No date define on the invoice %s, take the today '
                    'date in order to update the tax rate'%invoice.id)
                date = fields.date.context_today(self, cr, uid, context=context) 
            else:
                date = invoice.date_invoice
            for line in invoice.invoice_line:
                tax_ids = []
                need_to_update = False
                for tax in line.invoice_line_tax_id:
                    if tax_obj._check_tax_validity(cr, uid, tax,
                            date, context=context):
                        tax_ids.append(tax.id)
                    else:
                        new_tax_id = tax_obj._map_tax(cr, uid, tax,
                            date,
                            automatic_update=automatic_update,
                            context=context)
                        tax_ids.append(new_tax_id)
                        need_to_update = True
                if need_to_update:
                    line.write({'invoice_line_tax_id': [(6, 0, tax_ids)]})
            invoice.button_reset_taxes()
        return True

class account_tax(orm.Model):
    _inherit = 'account.tax'
    
    def _check_tax_validity(self, cr, uid, tax, date, raise_exception=False, context=None):
        if tax.valid_until and tax.valid_until < date:
            if raise_exception:
                raise orm.except_orm(_("User Error"),
                    _("The tax %s can be only use until the %s. Fix it")
                    %(tax.name, tax.valid_until))
            else:
                return False
        elif tax.valid_from and tax.valid_from > date:
            if raise_exception:
                raise orm.except_orm(_("User Error"),
                    _("The tax %s can be only use from the %s. Fix it")
                    %(tax.name, tax.valid_from))
            else:
                return False
        return True

    def _map_tax(self, cr, uid, tax, date, automatic_update=False, context=None):
        config_line_obj = self.pool.get('account.update.tax.config.line')
        domain = ['|',
            '&',
                ('sale_config_id.switch_date', '>', date),
                ('target_tax_id', '=', tax.id),
            '&',
                ('sale_config_id.switch_date', '<=', date),
                ('source_tax_id', '=', tax.id),
            ]
        if automatic_update:
            domain.append(('sale_config_id.automatic_tax_update', '=', True))
        line_id = config_line_obj.search(cr, uid, domain, context=context)

        if not line_id:
            raise orm.except_orm(_('Configuration Error'),
                    _('No mapping found for the tax %s')%tax.name)
        elif len(line_id) > 1:
            raise orm.except_orm(_('Configuration Error'),
                    _('Too many mapping found for the tax %s')%tax.name)
        else:
            line = config_line_obj.browse(cr, uid, line_id[0], context=context)
            if line.sale_config_id.switch_date <= date:
                return line.target_tax_id.id
            else:
                return line.source_tax_id.id
