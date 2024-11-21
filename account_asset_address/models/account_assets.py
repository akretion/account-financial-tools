# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AcountAsset(models.Model):

    _inherit = "account.asset"

    company_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Site de l'immobilisation",
        domain="[('id', 'in', company_partner_ids)]",
    )
    address_one_line = fields.Char(compute="_compute_address_line", store=True)
    company_partner_ids = fields.Many2many(
        comodel_name="res.partner", compute="_compute_child_partner_list"
    )

    @api.onchange("company_address_id")
    def _compute_address_line(self):
        line = ""
        for record in self:
            if record.company_address_id.street:
                line += record.company_address_id.street
            if record.company_address_id.street2:
                line += ", "
                line += record.company_address_id.street2
            if record.company_address_id.zip:
                line += ", "
                line += record.company_address_id.zip
            if record.company_address_id.city:
                line += " "
                line += record.company_address_id.city
            record.address_one_line = line

    @api.depends("company_id")
    def _compute_child_partner_list(self):
        for record in self:
            record.company_partner_ids = record.env["res.partner"].search(
                [("id", "child_of", record.company_id.partner_id.ids)]
            )

    @api.model
    def _xls_active_fields(self):
        list_field = super()._xls_active_fields()
        list_add_field = ["site_name", "address"]
        for field in list_add_field:
            list_field.append(field)
        return list_field
