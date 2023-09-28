from odoo import models, _
from ..util import VoodooUtility

class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'
    # _name = 'voodoo.stock_picking_inherited'

    def enqueue_voodooDeviceCall(self, dev_id,data):
        # Here you can get the component and call its method
        # You will need to get the record again as you are in a new transaction

        VoodooUtility.voodooDeviceCall(self,dev_id,data)


    def button_lights(self):

        # Your custom action goes here

        # Loop through each move in the picking
        for move in self.env['stock.move'].search([('picking_id', 'in', self.ids)]):
            # Generate line1 and line2 descriptions for the move

            name = move.product_id.display_name

            # Check if the source location has a voodoo_device_id
            dev_id = move.location_id.voodoo_device_id
            if dev_id:
                arrow = VoodooUtility.getArrow(move.location_id)

                data = {}
                data['command']='flash'
                data['arrow']=arrow
                data['line1']="PICK"
                if ' - ' in name:
                    line1, line2 = name.split(' - ', 1)
                    data['line2'] = line1
                    data['line3'] = line2
                else:
                    data['line2'] = name
                
                if move.product_uom_qty % 1 == 0:
                    data['quantity']= int(move.product_uom_qty)
                else:
                    data['line4'] = 'Qty: '+ str(move.product_uom_qty)
                
                data['nonce'] = 'moveid=' + str(move.id)
                self.with_delay(priority=0,max_retries=1).enqueue_voodooDeviceCall(dev_id,data)

            
            # Check if the destination location has a voodoo_device_id
            dev_id = move.location_dest_id.voodoo_device_id
            if dev_id:
                arrow = VoodooUtility.getArrow(move.location_dest_id)

                data = {}
                data['command']='flash'
                data['arrow']=arrow
                data['line1']="PUT"
                if ' - ' in name:
                    line1, line2 = name.split(' - ', 1)
                    data['line2'] = line1
                    data['line3'] = line2
                else:
                    data['line2'] = name


                if move.product_uom_qty % 1 == 0:
                    data['quantity']= int(move.product_uom_qty)
                else:
                    data['line4'] = 'Qty: '+ str(move.product_uom_qty)
                    
                data['nonce'] = 'moveid=' + str(move.id)
                self.with_delay(priority=0,max_retries=1).enqueue_voodooDeviceCall(dev_id,data)

        return