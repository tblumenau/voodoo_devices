{
    'name': 'Voodoo Devices',
    'version': '1.0',
    'category': 'Inventory Management',
    'summary': 'Add support for Voodoo Robotics cloud display devices',
    'depends': ['stock','stock_sms','queue_job', 'web'],
    'data': [
        'views/stock_location_view_extension.xml',
        'views/stock_picking_view_extension.xml',
        'views/res_config_settings_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'voodoo_devices/static/src/css/custom.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
