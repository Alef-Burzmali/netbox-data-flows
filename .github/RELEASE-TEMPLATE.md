Description

## Compatibility
NetBox: >=4.0.0
Python: 3.10

Use version 0.8 if you need compatibility with NetBox 3.7

## Update procedure
* Run NetBox's `upgrade.sh`, and restart NetBox

or

* Activate your NetBox virtual env: `source /opt/netbox/venv/bin/activate`
* Update the module code: `pip install --upgrade netbox-data-flows`
* Run the migrations: `/opt/netbox/netbox/manage.py migrate netbox_data_flows`
* Restart NetBox

## Changes
* ...


**Full Changelog**: https://github.com/Alef-Burzmali/netbox-data-flows/compare/v0.X.X...v0.X.X
