from odoo import models, _
from ..util import VoodooUtility


        
class StockPickingBatchInherited(models.Model):
    _inherit = 'stock.picking.batch'
    # _name = 'voodoo.stock_picking_inherited'

    def enqueue_voodooDeviceCall(self, dev_id,data):
        # Here you can get the component and call its method
        # You will need to get the record again as you are in a new transaction

        VoodooUtility.voodooDeviceCall(self,dev_id,data)


    def button_lights(self):

        # Your custom action goes here

        # Loop through each move in the picking
        pickings = self.mapped('picking_ids')
        for move in self.env['stock.move'].search([('picking_id', 'in', pickings.ids)]):
            # Generate line1 and line2 descriptions for the move

            VoodooUtility.processMove(self,move)

        return