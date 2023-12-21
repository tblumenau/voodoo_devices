{
    'name': 'Voodoo Devices',
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Enhance warehouse efficiency with this Odoo addon from Voodoo Robotics, seamlessly integrating IoT pick-to-light systems for optimized picking, putting, kitting, and more, streamlining operations with real-time guidance and automation.',
    'author': 'Voodoo Robotics',
    'website': 'https://voodoorobotics.com/',
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
    "images": ['static/images/banner.png', 'static/description/device.webp','static/description/screens.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
