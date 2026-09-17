{
    'name': 'Voodoo Pick to Light Devices',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Wireless pick to light (pick-to-light), put to light and put wall displays for Odoo Inventory. Light-directed picking, kitting and sortation with battery-powered devices from Voodoo Robotics. No wiring.',
    'author': 'Voodoo Robotics',
    'website': 'https://voodoorobotics.com/press-release/odoo-integration/',
#   Choose which line to uncomment below based on your use of batch or wave picking
#    'depends': ['stock','stock_sms','queue_job', 'web', 'stock_picking_batch', 'stock_picking_wave'],
#    'depends': ['stock','stock_sms','queue_job', 'web', 'stock_picking_batch'],
#    'depends': ['stock','stock_sms','queue_job', 'web', 'stock_picking_wave'],
    'depends': ['stock','stock_sms','queue_job', 'web'],
    
    
    'data': [
        'views/stock_location_view_extension.xml',
        'views/stock_picking_view_extension.xml',
        
#    Enable these if needed
#        'views/stock_picking_batch_view_extension.xml',
#        'views/stock_picking_wave_view_extension.xml',

        'views/res_config_settings_view.xml',
        'views/res_users_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'voodoo_devices/static/src/css/custom.css',
        ],
    },
    "images": ['static/images/banner.png', 'static/description/images/screens.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
