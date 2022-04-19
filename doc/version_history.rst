.. py:currentmodule:: lsst.ts.hvac

.. _lsst.ts.hvac.version_history:

###############
Version History
###############

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
