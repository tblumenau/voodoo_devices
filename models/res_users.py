from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    voodoo_device_color = fields.Selection(
        [('red', 'Red'), ('green', 'Green'), ('blue', 'Blue'), ('cyan', 'Cyan'), ('magenta','Magenta'), ('yellow','Yellow')],
        string='Voodoo Device Color',
        help='Select your preferred Voodoo Device Color.',
        required = True,
        default = 'red'
    )
    voodoo_device_beep = fields.Selection(
        [('disabled', 'Disabled'), ('15,c5,4', 'Enabled')],
        string='Voodoo Device Beep',
        help='Enable a beep when picking.',
        required = True,
        default = 'disabled'
    )

    voodoo_name = fields.Char(string='Voodoo Name', help ='Name to appear on Voodoo Device.  Leave blank to remove this line.')

    voodoo_seconds = fields.Integer(
        string='Voodoo Seconds',
        help='Set to non-zero value to override.',
        default=0, 
        required=True
    )

    @api.constrains('voodoo_seconds')
    def _check_voodoo_seconds(self):
        for user in self:
            if user.voodoo_seconds < 0:
                raise ValidationError("Voodoo Seconds cannot be negative!")