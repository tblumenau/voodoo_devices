# Odoo 18 Migration Notes for `voodoo_devices`

## Prerequisites
- **Odoo**: 18.0 (Community or Enterprise).
- **Python**: 3.10+ (match the Odoo 18 runtime).
- **queue_job**: 18.0-compatible release from OCA (install and add to `server_wide_modules` if you use job workers).
- **Workers**: enable workers in `odoo.conf` when using `queue_job`.

## Manual Steps
1. Update your addons path to include this module.
2. Ensure the OCA `queue_job` addon is installed and listed in `server_wide_modules` (e.g., `web,queue_job`).
3. Review and update the dependency list if you previously used `stock_sms` (this module no longer requires it).
4. Configure **Settings → Voodoo Devices** with the endpoint URL, username, and password.
5. If using batch or wave picking, uncomment the relevant model and view extensions in the addon.

## Rollback Plan
1. Uninstall the `voodoo_devices` addon from Apps.
2. Restore the previous addon version from backup (including prior manifest/configuration).
3. Restart Odoo and verify that `queue_job` workers return to their previous configuration.
4. Reinstall the previous addon version if needed and reapply your previous settings.
