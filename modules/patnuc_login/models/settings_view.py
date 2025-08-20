# models.py

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_login_logo = fields.Binary(string="Logo")
    custom_login_background_color = fields.Char(string="Couleur de fond")
    custom_login_background_image = fields.Binary(string="Image de fond")
    custom_login_name = fields.Char(string="Nom de l'application")
    custom_login_sigle = fields.Char(string="Sigle de l'application")
    custom_login_version = fields.Char(string="Version de l'application")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_param = self.env['ir.config_parameter'].sudo()
        res.update(
            custom_login_logo=config_param.get_param('custom_login_logo', default=''),
            custom_login_background_color=config_param.get_param('custom_login_background_color', default='#FFFFFF'),
            custom_login_background_image=config_param.get_param('custom_login_background_image', default=''),
            custom_login_name=config_param.get_param('custom_login_name', default='Odoo'),
            custom_login_sigle=config_param.get_param('custom_login_sigle', default='O.d.o.o'),
            custom_login_version=config_param.get_param('custom_login_version', default='1.0')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('custom_login_logo', self.custom_login_logo or '')
        config_param.set_param('custom_login_background_color', self.custom_login_background_color or '#FFFFFF')
        config_param.set_param('custom_login_background_image', self.custom_login_background_image or '')
        config_param.set_param('custom_login_name', self.custom_login_name or 'Odoo')
        config_param.set_param('custom_login_sigle', self.custom_login_sigle or 'O.d.o.o')
        config_param.set_param('custom_login_version', self.custom_login_version or '1.0')
