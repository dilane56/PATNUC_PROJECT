# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _render_template(self, template, values=None):
        # if template in ['web.login', 'web.webclient_bootstrap']:
        if not values:
            values = {}
        values["title"] = "ERP - patnuc"
        return super(IrUiView, self)._render_template(template, values)

        