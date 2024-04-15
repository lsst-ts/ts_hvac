.. py:currentmodule:: lsst.ts.hvac

.. _lsst.ts.hvac:

############
lsst.ts.hvac
############

Controller for the HVAC (Heating, Ventilation and Air Conditioning) system at Vera C. Rubin Observatory.

Using lsst.ts.hvac
====================

.. toctree::
    csv_and_xml
    mqtt
    :maxdepth: 1

Usage
-----

The primary class is:

* `HvacCsc`: controller for the HVAC system.

Apart from that there is the hvac_mqtt_to_SAL_XML.py script which contains several functions for parsing the input CSV file and for processing the MQTT topics and items and their data types, limit and units.

Run the ``HVAC`` controller  using ``bin/run_hvac.py``.

.. _building single package docs: https://developer.lsst.io/stack/building-single-package-docs.html

Contributing
============

``lsst.ts.hvac`` is developed at https://github.com/lsst-ts/ts_hvac.
You can find Jira issues for this module under the `ts_hvac <https://rubinobs.atlassian.net/issues/?jql=project%20%3D%20DM%20AND%20labels%20%3D%20ts_hvac>`_ label.

Python API reference
====================

.. automodapi:: lsst.ts.hvac
   :no-main-docstr:

Version History
===============

.. toctree::
    version_history
    :maxdepth: 1
