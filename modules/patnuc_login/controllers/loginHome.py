
import ast
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.home import SIGN_UP_REQUEST_PARAMS 
import pytz
import datetime
import logging

import odoo
import odoo.modules.registry
from odoo import http
from odoo.http import request
_logger = logging.getLogger("++++++++++++++++++++++++")




#----------------------------------------------------------
# Odoo Web web Controllers
#----------------------------------------------------------
class LoginHomePatnuc(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):

        SIGN_UP_REQUEST_PARAMS.update({'custom_login_name'}),
        SIGN_UP_REQUEST_PARAMS.update({'custom_login_version'}),
        SIGN_UP_REQUEST_PARAMS.update({'custom_login_logo'}),
        SIGN_UP_REQUEST_PARAMS.update({'custom_login_sigle'})

        _logger.info('+++++++++++++++++++++ SIGN_UP_REQUEST_PARAMS',SIGN_UP_REQUEST_PARAMS)
        
        param_obj = request.env['ir.config_parameter'].sudo()
        
        request.params['custom_login_name'] = param_obj.get_param('custom_login_name') or False
        request.params['custom_login_version'] = param_obj.get_param('custom_login_version') or False
        request.params['custom_login_logo'] = param_obj.get_param('custom_login_logo') or False
        request.params['custom_login_sigle'] = param_obj.get_param('custom_login_sigle') or False
        response = super(LoginHomePatnuc, self).web_login(redirect, **kw)

        return response