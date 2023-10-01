# voodoo_devices
Integration addon for Voodoo Robotics Pick To Light cloud display devices with Odoo

Please note that if you're using BATCH or WAVE picking, there are three things you need to adjust:

1) in the __manifest__.py file, you must select a 'depends' line appropriate for your situation.
2) in the __manifest__.py file, you must uncomment any view_extension.xml line needed for your GUI.
3) in the models/__init__.py file, you need to uncomment the lines to support your picking type.

After activating this addon, you need to enter your Voodoo Devices credentials in the Settings panel and, if you're using feedback, you need to enter your Odoo credentials on you BigBlock server under the Setting tab.

Since this addon depends on the queue_job addon, you may need to add the following to your odoo.conf file:


```
# select a value appropriate for your situation
workers = 4
server_wide_modules = web,queue_job
```