from odoo import models, fields, api

class FishingPermitReject(models.TransientModel):
    _name = 'fishing.permit.reject'
    _description = 'Wizard de Rejet de Permis de Pêche'

    rejection_reason = fields.Text(string='Motif de rejet', required=True)
    permit_id = fields.Many2one('fishing.permit', string='Permis', required=True)

    def action_reject_permit(self):
        """Action pour rejeter le permis et mettre à jour l'enregistrement principal."""
        self.ensure_one()
        permit = self.permit_id
        permit.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })
        permit.message_post(body=f"La demande de permis de pêche a été rejetée. Motif : {self.rejection_reason}")
        return {'type': 'ir.actions.act_window_close'}