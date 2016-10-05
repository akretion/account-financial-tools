# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, exceptions, fields, models, _


class WizAccountAssetReport(models.TransientModel):

    _name = 'wiz.account.asset.report'
    _description = 'Financial Assets report'

    fiscalyear_id = fields.Many2one(
        'date.range', 'Fiscal Year', required=True)
    parent_asset_id = fields.Many2one(
        'account.asset', 'Asset Filter',
        domain=[('type', '=', 'view')])

    @api.multi
    def xls_export(self):
        self.ensure_one()
        asset_obj = self.env['account.asset']
        parent_asset_id = self.parent_asset_id.id
        if not parent_asset_id:
            parents = asset_obj.search(
                [('type', '=', 'view'), ('parent_id', '=', False)])
            if not parents:
                raise exceptions.UserError(
                    _("No top level asset of type 'view' defined!"))
            else:
                parent_asset = parents[0]

        # sanity check
        errors = asset_obj.search(
            [('type', '=', 'normal'), ('parent_id', '=', False)])
        for error in errors:
            error_name = error.name
            if error.code:
                error_name += ' (' + error.code + ')' or ''
            raise exceptions.UserError(
                _("No parent asset defined for asset '%s'!") % error_name)

        domain = [('type', '=', 'normal'), ('id', 'child_of', parent_asset_id)]
        assets = asset_obj.search(domain)
        if not assets:
            raise exceptions.ValidationError(
                _('No records found for your selection!'))

        datas = {
            'model': 'account.asset',
            'fiscalyear_id': self.fiscalyear_id.id,
            'ids': [parent_asset_id],
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account.asset.xls',
                'datas': datas}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
