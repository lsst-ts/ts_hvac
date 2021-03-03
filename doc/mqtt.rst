.. py:currentmodule:: lsst.ts.hvac

.. _lsst.ts.hvac-MQTT:

####
MQTT
####

This page is not for describing the MQTT protocol.
There are much better pages for that, for instance on https://en.wikipedia.org/wiki/MQTT
This page aims to describe how MQTT is used for the HVAC system at Rubin Observatory.

MQTT topics
-----------

A typical HVAC MQTT topic is constructed as follows: LSST/<floor>/<component>/<item> with <floor>, <component> and <item> generally, but not always, in Spanish.
Some examples are:

* LSST/PISO02/FANCOIL01/ESTADO_OPERACION
* LSST/PISO02/FANCOIL03/SETPOINT_COOLING_NIGHT
* LSST/PISO04/MANEJADORA/GENERAL/SBLANCA/ESTADO_DAMPER

Note that in the last case, component is taken as "MANEJADORA/GENERAL/SBLANCA".
An item always is the part after the last forward slash in the topic string.

Telemetry updates
-----------------

When the HVAC CSC (or any other MQTT client) connects, the HVAC system will report the full status of all components.
Then the individual components will send updated values for their items at a frequency specific for each item.
The HVAC CSC will collect the updated values and computes a median over each with a configurable frequency which defaults to 60 seconds.
