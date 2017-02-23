# -*- coding: utf-8 -*-
###############################################################################
#
#   account_writeoff_autodelete for OpenERP
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

    def reconcile(self, *args, **kwargs):
        context = kwargs.get('context')
        if context is None:
            ctx={}
        else:
            ctx = context.copy()
        ctx['reconcile_mode'] = True
        kwargs['context'] = ctx
        res = super(account_move_line, self).reconcile(*args, **kwargs)


class account_move(osv.Model):
    _inherit = "account.move"

    _columns = {
        'writeoff': fields.boolean('WriteOff'),
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        if context.get('reconcile_mode'):
            vals['writeoff'] = True
        return super(account_move, self).create(cr, uid, vals, context=context)


class account_move_reconcile(osv.Model):
    _inherit = "account.move.reconcile"

    def unlink(self, cr, uid, ids, context=None):
        ids = list(set(ids))
        move_obj = self.pool.get('account.move')
        for rec in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in rec.line_id:
                if line.move_id.writeoff and not line.move_id.id in move_ids:
                    move_ids.append(line.move_id.id)
            super(account_move_reconcile, self).unlink(cr, uid, [rec.id], context=context)
            if move_ids:
                move_obj.button_cancel(cr, uid, move_ids, context=context)
                move_obj.unlink(cr, uid, move_ids, context=context)
        return True

