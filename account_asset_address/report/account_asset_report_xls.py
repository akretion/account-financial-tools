# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import FORMATS


class AssetReportXlsx(models.AbstractModel):
    _inherit = "report.account_asset_management.asset_report_xls"

    def _get_asset_template(self):
        template = super()._get_asset_template()
        template.update(
            {
                "site_name": {
                    "header": {
                        "type": "string",
                        "value": self._("Site"),
                        "format": FORMATS["format_theader_yellow_center"],
                    },
                    "asset": {
                        "type": "string",
                        "value": self._render("asset.company_address_id.name or ''"),
                        "format": FORMATS["format_tcell_center"],
                    },
                    "width": 40,
                },
                "address": {
                    "header": {
                        "type": "string",
                        "value": self._("Address"),
                        "format": FORMATS["format_theader_yellow_center"],
                    },
                    "asset": {
                        "type": "string",
                        "value": self._render("asset.address_one_line or ''"),
                        "format": FORMATS["format_tcell_center"],
                    },
                    "width": 40,
                },
            }
        )

        return template
