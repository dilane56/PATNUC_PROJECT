from odoo import models, fields

class HomologationRejetWizard(models.TransientModel):
    _name = 'homologation.rejet.wizard'
    _description = 'Wizard pour le motif de rejet des demandes d\'homologation'

    rejection_reason = fields.Text(string="Motif de rejet", required=True)

    def action_rejeter_demande(self):
        """
        Applique le rejet et le motif sur l'enregistrement de la demande d'homologation.
        """
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:

            request = self.env['homologation.request'].browse(active_id)

            # Mettre à jour l'état et le motif de rejet sur l'enregistrement permanent
            request.write({
                'state': 'rejected',
                'rejection_reason': self.rejection_reason
            })

            request.message_post(body=f"Demande d'homologation rejetée avec le motif suivant : {self.rejection_reason}")

        return {'type': 'ir.actions.act_window_close'}