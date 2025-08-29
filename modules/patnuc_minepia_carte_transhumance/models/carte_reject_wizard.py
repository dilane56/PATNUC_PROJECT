from odoo import models, fields


class CarteRejetWizard(models.TransientModel):
    _name = 'carte.rejet.wizard'
    _description = 'Wizard pour le motif de rejet des cartes de transhumance'

    rejection_reason = fields.Text(string="Motif de rejet", required=True)

    def action_rejeter_demande(self):
        """
        Applique le rejet et le motif sur l'enregistrement de la demande de carte de transhumance.
        """
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            request = self.env['carte.transhumance'].browse(active_id)
            request.write({'state': 'rejected', 'rejection_reason': self.rejection_reason})
            request.message_post(
                body=f"Demande de carte de transhumance rejetée avec le motif suivant : {self.rejection_reason}")
        return {'type': 'ir.actions.act_window_close'}