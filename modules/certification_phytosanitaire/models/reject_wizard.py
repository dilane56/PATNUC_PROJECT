# Dans rejet_wizard.py

from odoo import models, fields


class RejetWizard(models.TransientModel):
    _name = 'rejet.wizard'
    _description = 'Wizard pour le motif de rejet'

    rejection_reason = fields.Text(string="Motif de rejet", required=True)

    def action_rejeter_demande(self):
        """
        Applique le rejet et le motif sur l'enregistrement de la demande.
        """
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            # Récupérer l'enregistrement de la demande de certification
            request = self.env['certification.request'].browse(active_id)

            # Écrire les valeurs de l'état et du motif sur l'enregistrement principal
            request.write({
                'state': 'rejected',
                'rejection_reason': self.rejection_reason
            })

            request.message_post(body=f"Demande rejetée avec le motif suivant : {self.rejection_reason}")

        return {'type': 'ir.actions.act_window_close'}