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

{
    'name': 'account_reconcile_set_partner',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """Want a move line without partner is reconcile
    with a move line without partner the partner is set automatically
    on the move line""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['account'], 
    'init_xml': [],
    'update_xml': [ 
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
