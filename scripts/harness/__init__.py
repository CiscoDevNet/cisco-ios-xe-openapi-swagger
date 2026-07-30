"""Track B C9K RESTCONF capture harness (dev-only, GET phase).

Not wired into build_release.py, CI, or the Pages deploy. See DEVICE_DATA_COLLECTION.md.
Strictly READ-ONLY: all device access goes through request.restconf_get, which
hard-refuses any non-GET method. The CRUD phase (§7) is intentionally absent.
"""
