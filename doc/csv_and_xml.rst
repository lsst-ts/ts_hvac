.. py:currentmodule:: lsst.ts.hvac

.. _lsst.ts.hvac-CSV_and_XML:

###########
CSV and XML
###########

CSV
---

The Rubin Observatory HVAC system was implemented by DatControl who also provided an Excel sheet with the full information about the HVAC system.
This includes the names of the HVAC components and the data type, limits and units of the telemetry published.
This information is necessary for validation purposes since the :doc:`mqtt` protocol doesn't provide that information.
The individual sheets in the Excel sheet have manually been merged into a single sheet which was exported to CSV.
This CSV file can be found in the python/data directory and serves as input for several operations:

* To read all MQTT topics
* To read the data types, limits and units for all MQTT topics

The data read from the CSV file are kept in memory and are used for all operations provided by the ts_hvac project:

* Create the XML files describing the Commands, Events and Telemetry which get used in ts_xml.
* Verify the received MQTT messages by the HVAC CSC and compute medians of the received telemetry.
* Simulate the publication of HVAC telemetry and the reception of HVAC commands by the simulator.
* Unit testing of the CSC and simulator.

The columns in the CSV file are:

* floor
* subsystem
* variable
* topic_and_item
* publication
* subscription
* signal
* rw
* range
* limits
* unit
* state
* observations
* notes

where "rw" means Read or Write.

XML
---

In order to automatically create the Commands, Events and Telemetry XML files for ts_xml, several functions were developed.
These functions parse the CSV file and, based on a simple principle, detect which components are present in the HVAC system.
The principle is that all HVAC components support receiving a command to be switched on or off, apart from three components which are called Bomba Agua Fria (Cold Water Pump), General and Valvula (Valve).

Based on this principle all components in the HVAC system are identified and the MQTT topics are split up in components and their items.
While reading the MQTT information, the data type, limits and unit of each item for each component are identified and also if an item is telemetry (read) or a command (write).
Finally, in case of a command item a distinction is made between enable commands (one per component except the three mentioned above) and configuration commands (all others).

Some of the functions for reading the CSV file are also used by the HVAC CSC, the simulator and unit tests to avoid an overhead of code that can be generated automatically.

See :doc:`mqtt` for more details about the MQTT protocol and the HVAC topics.
