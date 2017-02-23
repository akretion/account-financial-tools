# -*- coding: utf-8 -*-
###############################################################################
#
#   module for OpenERP
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import osv, fields

class account_move_line(osv.Model):
    _inherit = "account.move.line"

    _columns = {
        'partner_set_automatically': fields.boolean('Partner set automatically'),
    }

    def reconcile(self, cr, uid, ids, *args, **kwargs):
        context = kwargs.get('context')
        if context is None:
            ctx={}
        else:
            ctx = context.copy()
        ctx['reconcile_mode'] = True
        kwargs['context'] = ctx
        partner_id = False
        line2update = []
        for line in self.browse(cr, uid, ids, context=context):
            if not line.partner_id:
                line2update.append(line)
            else:
                partner_id = line.partner_id.id
        if partner_id:
            for line in line2update:
                line.write({
                    'partner_id': partner_id,
                    'partner_set_automatically': True,
                })
        res = super(account_move_line, self).reconcile(cr, uid, ids, *args, **kwargs)

class account_move_reconcile(osv.Model):
    _inherit = "account.move.reconcile"

    def unlink(self, cr, uid, ids, context=None):
        ids = list(set(ids))
        move_obj = self.pool.get('account.move')
        for rec in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in rec.line_id:
                if line.partner_set_automatically:
                    line.write({
                        'partner_id': False,
                        'partner_set_automatically':False
                    })
            super(account_move_reconcile, self).unlink(cr, uid, [rec.id], context=context)
        return True

