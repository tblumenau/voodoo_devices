from odoo import api, models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    # _name = 'voodoo.settings'

    endpoint_url = fields.Char(string='Voodoo Endpoint URL',default='https://www.voodoodevices.com/api/',help="Should end in /api/")
    username = fields.Char(string='Username',default='myusername')
    password = fields.Char(string='Password',default='mypassword')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            endpoint_url=ICPSudo.get_param('voodoo.endpoint_url'),
            username=ICPSudo.get_param('voodoo.username'),
            password=ICPSudo.get_param('voodoo.password'),
        )
        return res

    def set_values(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('voodoo.endpoint_url', self.endpoint_url or '')
        ICPSudo.set_param('voodoo.username', self.username or '')
        ICPSudo.set_param('voodoo.password', self.password or '')
        super(ResConfigSettings, self).set_values()