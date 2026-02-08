from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    # _name = 'voodoo.settings'

    endpoint_url = fields.Char(
        string='Voodoo Endpoint URL',
        default='https://www.voodoodevices.com/api/',
        help="Should end in /api/",
        config_parameter='voodoo.endpoint_url',
    )
    username = fields.Char(
        string='Username',
        default='myusername',
        config_parameter='voodoo.username',
    )
    password = fields.Char(
        string='Password',
        default='mypassword',
        config_parameter='voodoo.password',
    )
