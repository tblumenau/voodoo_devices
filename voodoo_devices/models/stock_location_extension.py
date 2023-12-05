import re
import asyncio

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ..util import VoodooUtility

import logging

_logger = logging.getLogger(__name__)


class StockLocationInherited(models.Model):
    _inherit = 'stock.location'
    # _name = 'voodoo.stock_location_inherited'

    voodoo_device_id = fields.Char(string="Voodoo Device ID")
    voodoo_device_orientation = fields.Selection([
        ('above',"Device is above location"),
        ('below',"Device is below location"),
        ('left',"Device is to the left of location"),
        ('right',"Device is to the right of location"),
        ('aboveright',"Device is above and to the right of location"),
        ('aboveleft',"Device is above and to the left of location"),
        ('belowright',"Device is below and to the right of location"),
        ('belowleft',"Device is below and to the left of location"),
    ], string="Voodoo Device Orientation", default='below')

    _sql_constraints = [
        ('voodoo_device_id_voodoo_device_orientation_unique', 'UNIQUE(voodoo_device_id, voodoo_device_orientation)', 'The combination of Device ID and Orientation must be unique for each location! Make sure this Device is not listed/placed elsewhere in your system.')
    ]

    @api.constrains('voodoo_device_id')
    def _check_voodoo_device_id(self):
        pattern = re.compile("^[0-9a-fA-F]{6}:[0-9a-fA-F]{6}$")

        for record in self:
            if record.voodoo_device_id and not pattern.match(record.voodoo_device_id):
                raise ValidationError(_("Invalid Voodoo Device ID."))
            
    
    # def write(self, vals):
    #     name_or_parent_changed = 'name' in vals or 'location_id' in vals
    #     res = super(StockLocationInherited, self).write(vals)
    #     if name_or_parent_changed:
    #         for location in self:
    #             self._handle_location_change(location)
    #     return res  

    def enqueue_redo_statics(self, voodoo_ids):

        VoodooUtility.redoStatics(self,voodoo_ids)

    def write(self, vals):
        # Step 1: Extract current voodoo_device_id values from the records in self
        # and their child locations
        current_voodoo_ids = set(self.mapped('voodoo_device_id'))
        current_voodoo_ids.update(self.mapped('child_ids.voodoo_device_id'))
        
        # Call super() to apply the changes
        result = super(StockLocationInherited, self).write(vals)
        
        # Step 3: Extract the voodoo_device_id values again from self and child locations,
        # as they may have changed
        updated_voodoo_ids = set(self.mapped('voodoo_device_id'))
        updated_voodoo_ids.update(self.mapped('child_ids.voodoo_device_id'))
        
        # Step 4: Check if voodoo_device_id is in vals
        if 'voodoo_device_id' in vals:
            updated_voodoo_ids.add(vals['voodoo_device_id'])
        
        # Step 5: Combine the current and updated voodoo_device_id values into a set
        all_voodoo_ids = current_voodoo_ids.union(updated_voodoo_ids)
        
        # Now all_voodoo_ids contains all relevant voodoo_device_id values
        # from the locations in self and their child locations.

        # Perform any additional operations or checks based on all_voodoo_ids
        self.with_delay(priority=0,max_retries=1).enqueue_redo_statics(list(all_voodoo_ids))

        return result
    
    @api.model_create_multi
    def create(self, vals_list):
        # Step 1: Extract voodoo_device_id values from vals_list
        new_voodoo_ids = set(vals.get('voodoo_device_id') for vals in vals_list)
        
        # Call super() to create the records
        records = super(StockLocationInherited, self).create(vals_list)
        
        # Step 2: Extract the voodoo_device_id values from the created records
        # and their child locations
        
        # Perform any additional operations or checks based on all_voodoo_ids
        self.with_delay(priority=0,max_retries=1).enqueue_redo_statics(list(new_voodoo_ids))

        return records
    
    def unlink(self):
        # Step 1: Extract voodoo_device_id values from the records in self
        # and their child locations before they are deleted
        current_voodoo_ids = set(self.mapped('voodoo_device_id'))
        current_voodoo_ids.update(self.mapped('child_ids.voodoo_device_id'))
        
        # Call super() to delete the records
        result = super(StockLocationInherited, self).unlink()
        
        # After the super() call, the records are deleted, so no further extraction is needed
        
        # Perform any additional operations or checks based on current_voodoo_ids
        self.with_delay(priority=0,max_retries=1).enqueue_redo_statics(list(current_voodoo_ids))

        return result