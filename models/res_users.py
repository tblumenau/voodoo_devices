from odoo import api, fields, models

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
