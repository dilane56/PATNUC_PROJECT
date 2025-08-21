from odoo import models, http
from odoo.http import request
import time

class SessionTimeout(models.Model):
    _inherit = 'res.users'

    @http.route('/web/session/check', type='json', auth='user')
    def check_session(self):
        # Vérifier la durée d'inactivité
        if request.session.get('last_activity'):
            last_activity = request.session['last_activity']
            if time.time() - last_activity > 300:  # 5 minutes
                request.session.logout()
                return {'expired': True}
        request.session['last_activity'] = time.time()
        return {'expired': False}