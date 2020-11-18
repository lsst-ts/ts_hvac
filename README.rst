``ts_HVAC`` is a CSC that controls the HVAC system via MQTT messages. It also contains components to generate the HVAC SAL XML files.

This code uses ``pre-commit`` to maintain ``black`` formatting and ``flake8`` compliance.
To enable this:

* Run ``pre-commit install`` once.
* If directed, run ``git config --unset-all core.hooksPath`` once.
