# Odoo 19 Migration Guide for Voodoo Devices

## Prerequisites
- **Odoo**: 19.0 (community or enterprise).
- **Python**: 3.12 (per Odoo 19 requirements).
- **queue_job**: OCA `queue_job` 19.0 (must be installed/enabled because this addon uses `with_delay`).
- **Optional stock modules**: install `stock_picking_batch` and/or `stock_picking_wave` only if you enable the related views/models in this addon.

## Manual Steps
1. **Update dependencies**: ensure `queue_job` is installed and compatible with Odoo 19.
2. **Update addons list**: restart Odoo and update the app list.
3. **Install/upgrade the addon**: upgrade `voodoo_devices` from Apps.
4. **Re-enter credentials**: open *Settings → Voodoo Devices* and confirm the endpoint, username, and password.
5. **Validate user preferences**: verify each user has a `Voodoo Device Color`, `Voodoo Device Beep`, and `Voodoo Seconds` configured.
6. **Optional batch/wave support**: if using picking batches or waves, uncomment the related `depends` and model imports, then upgrade the addon.

## Rollback Plan
1. **Uninstall the addon**: remove `voodoo_devices` from Apps.
2. **Disable queue jobs**: stop workers or disable `queue_job` to prevent background tasks.
3. **Restore database backup**: revert to the pre-migration snapshot if needed.
4. **Restart Odoo**: clear caches and confirm baseline stock operations work.
