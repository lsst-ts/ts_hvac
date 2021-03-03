.. py:currentmodule:: lsst.ts.hvac

.. _lsst.ts.hvac.version_history:

###############
Version History
###############

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
