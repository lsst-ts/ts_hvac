.. py:currentmodule:: lsst.ts.hvac

.. _lsst.ts.hvac.version_history:

###############
Version History
###############

v0.17.0
=======

* Add OperatingMode and UnitState enums.
* Translate all Spanish to English.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* ts_xml 22.1

v0.16.0
=======

* Update the Jira URL in index.rst.
* Fix the conda recipe.
* Add a unit test for the MqttClient class.
* Add glycol sensor telemetry.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 20.4

v0.15.1
=======

* Update the version of ts-conda-build to 0.4 in the conda recipe.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 20.0

v0.15.0
=======

* Switch from ts_idl to ts_xml.
* Extract BaseMqttClient interface.
* Make sure to disconnect when going to FAULT state.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 20.0

v0.14.0
=======

* Add HVAC events.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 20.0

v0.13.2
=======

* Remove XML 16 overrides.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 19.0

v0.13.1
=======

* Move non-XML dicts to this project.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 19.0

v0.13.0
=======

* Remove XML files that get generated.
* Add Dynalene commands and related events.

Requires:

* ts_salobj 7
* ts_idl 4.6
* ts_utils
* IDL files for HVAC from ts_xml 19.0

v0.12.0
=======

* Add more Dynalene events and telemetry.

Requires:

* ts_salobj 7
* ts_idl 4.4
* ts_utils 1
* IDL files for HVAC from ts_xml 18.0

v0.11.1
=======

* Fix telemetry data type.

Requires:

* ts_salobj 7.0
* ts_idl 4.4
* ts_utils 1.0
* IDL files for HVAC from ts_xml 17.0

v0.11.0
=======

* Update HVAC CSV file with topics and items.
* Adjust generation of HVAC XML files to updated CSV file.
* Adjust simulator to updated CSV file.
* Adjust CSC to updated CSV file.

Requires:

* ts_salobj 7.0
* ts_idl 4.4
* ts_utils 1.0
* IDL files for HVAC from ts_xml 17.0

v0.10.1
=======

* Use ts_pre_commit_conf.
* Modernize Jenkinsfile.
* Add workaround for unknown topics and items
* Make all SAL methods async.

Requires:

* ts_salobj 7.0
* ts_idl 4.4
* ts_utils 1.0
* IDL files for HVAC from ts_xml 16.0

v0.10.0
=======

* Add Dynalene telemetry and events.
* Convert all pressure telemetry values from bar or PSI to Pa.

Requires:

* ts_salobj 7.0
* ts_idl 4.4
* ts_utils 1.0
* IDL files for HVAC from ts_xml 16.0

v0.9.4
======

* Update pre-commit hook versions.
* Remove `pip install` step since the dependencies were added to ts-develop.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.9.3
======

* Clean up workarounds.
* Improve exception logging.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.9.2
======

* Update pre-commit dependencies.
* Capture MqttClient logs to EFD now as well.
* Add try/except to prevent the CSC from stopping processing data.
* Improve handling of payloads that cannot be decoded by JSON.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.9.1
======

* Switch conda test command from py.test to pytest.
* Restore pytest plugins.
* Fix error handling status telemetry containing the string 'AUTOMATICO'.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.9.0
======

* Sort imports with isort.
* Install new pre-commit hooks.
* Add MyPy support.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.8.1
======

* Handle error situations better.
* Improve endpoint implementation.
* Prepare conda recipe for builds with multiple Python versions.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.8.0
======

* Modernize pre-commit config versions.
* Move the data directory to within the package directory.
* Switch to pyproject.toml.
* Use entry_points instead of bin scripts.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.7.1
======

* Reduce excessive logging.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.7.0
======

* Prepare for salobj 7.

Requires:

* ts_salobj 7.0
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 11.0

v0.6.0
======

* Replaced the use of ts_salobj functions with ts_utils functions.
* Added auto-enable capability.
* Converted the CSC to a non-configurable CSC.

Requires:

* ts_salobj 6.3
* ts_idl 3.1
* ts_utils 1.0
* IDL files for HVAC from ts_xml 9.2

v0.5.0
======

Rewrote the generation of the ts_xml XML files consolidating the commands and adding events.
Rewrote the CSC and unit tests to take into account the changes in the commands and the added events.
Removed the 'perc' prefix from command and telemetry enum items with a 'percentage' unit to accomodate better ts_xml item names.
Removed support for reading the HVAC configuration items from a JSON file.
Adopted the code to the latest version of the CSV file.
Improved the way the status transitions to and from DISABLED and ENABLED are handled.

Requires:

* ts_salobj 6.3
* ts_idl 3.1
* IDL files for HVAC from ts_xml 9.2


v0.4.0
======

Removed asynctest.
Upgraded Black to version 20.8b1.
Upgraded ts-conda-build to version 0.3.


Requires:

* ts_salobj 6.3
* ts_idl 3.1
* IDL files for HVAC from ts_xml 8.0


v0.3.0
======

Added support for reading the HVAC configuration items from a JSON file.


Requires:

* ts_salobj 6.3
* ts_idl 3.1
* IDL files for HVAC from ts_xml 8.0


v0.2.0
======

Added documentation to the project.


Requires:

* ts_salobj 6.3
* ts_idl
* IDL files for HVAC from ts_xml 7.0


v0.1.0
======

First release of the HVAC CSC.

This version already includes many useful things:

* Code that generates the ts_xml files for ts_hvac using a CSV file as input.
* A functioning HVAC CSC which can connect to the HVAC MQTT server on the summit and report telemetry based on the MQTT messages received.
* A basic simulator that produces MQTT messages with random values within the limits for each variable in the sub-systems.


Requires:

* ts_salobj 6.1
* ts_idl
* IDL files for HVAC from ts_xml 7.0
