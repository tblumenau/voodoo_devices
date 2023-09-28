from odoo import models, api
from ..util import VoodooUtility
import logging

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # _name = 'voodoo.stock_quant_inherited'


    def enqueue_redo_statics(self, voodoo_ids):

        VoodooUtility.redoStatics(self,voodoo_ids)



    @api.model_create_multi
    def create(self, vals_list):
        # Extract voodoo_device_id values from related locations before record creation
        location_ids = [vals.get('location_id') for vals in vals_list]
        current_voodoo_ids = set(self.env['stock.location'].browse(location_ids).mapped('voodoo_device_id'))
        
        # Call super() to create the records
        records = super(StockQuant, self).create(vals_list)
        
        
        # Perform additional operations or checks based on all_voodoo_ids
        self.with_delay(priority=0,max_retries=1).enqueue_redo_statics(list(current_voodoo_ids))

        return records
    

    def write(self, vals):
        # Extract current voodoo_device_id values from related locations before updating
        current_voodoo_ids = set(self.mapped('location_id.voodoo_device_id'))
        
        # Call super() to update the records
        result = super(StockQuant, self).write(vals)
        
        # Extract voodoo_device_id values from related locations after updating
        updated_voodoo_ids = set(self.mapped('location_id.voodoo_device_id'))
        
        # Combine the current and updated voodoo_device_id values into a set
        all_voodoo_ids = current_voodoo_ids.union(updated_voodoo_ids)
        
        # Perform additional operations or checks based on all_voodoo_ids
        self.with_delay(priority=0,max_retries=1).enqueue_redo_statics(list(all_voodoo_ids))

        return result

    def unlink(self):
        # Extract voodoo_device_id values from related locations before deletion
        current_voodoo_ids = set(self.mapped('location_id.voodoo_device_id'))
        
        # Call super() to delete the records
        result = super(StockQuant, self).unlink()
        
        # Perform additional operations or checks based on current_voodoo_ids, as the records are deleted after super()
        self.with_delay(priority=0,max_retries=1).enqueue_redo_statics(list(current_voodoo_ids))

        return result