# This file is part of ts_hvac.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from lsst.ts.xml.component_info import ComponentInfo

tick_script_template = """HVAC-{name}-Alarm

=====================================
var db = 'efd'
var rp = 'autogen'
var measurement = 'lsst.sal.HVAC.{topic}'
var groupBy = []
var whereFilter = lambda: {where}
var name = 'HVAC {name} Alarm'
var idVar = name
var message = '{{{{ if eq .Level "OK" }}}}Summit EFD HVAC {name} is back to normal.{{{{ else }}}}Summit EFD
HVAC {name} alarm. The monitored values are {monitored_values}.
<PUT SLACK USER IDS HERE> please check.{{{{ end }}}}'
var idTag = 'alertID'
var levelTag = 'level'
var messageField = 'message'
var durationField = 'duration'
var outputDB = 'chronograf'
var outputRP = 'autogen'
var outputMeasurement = 'alerts'
var triggerType = 'threshold'

var data = stream
    |from()
        .database(db)
        .retentionPolicy(rp)
        .measurement(measurement)
        .groupBy(groupBy)
        .where(whereFilter)

var trigger = data
    |alert()
        .crit(lambda: {crit})
        .stateChangesOnly()
        .message(message)
        .id(idVar)
        .idTag(idTag)
        .levelTag(levelTag)
        .messageField(messageField)
        .durationField(durationField)
        .post('<PUT SQUADCAST URL HERE>')
        .slack()
        .workspace('HVAC-alerts')
        .channel('#hvac-alerts')

trigger
    |eval({eval})
        .as({as_str})
        .keep()
    |influxDBOut()
        .create()
        .database(outputDB)
        .retentionPolicy(outputRP)
        .measurement(outputMeasurement)
        .tag('alertName', name)
        .tag('triggerType', triggerType)

trigger
    |httpOut('output')
=====================================
"""

ci = ComponentInfo(name="HVAC", topic_subname="")
topics_with_alarms: dict[str, set[str]] = {}
for topic in ci.topics:
    ti = ci.topics[topic]
    for field in ti.fields:
        if "alarm" in field.lower() or "warn" in field.lower():
            if topic not in topics_with_alarms:
                topics_with_alarms[topic] = set()
            topics_with_alarms[topic].add(field)

for topic in topics_with_alarms:
    efd_topic = topic.replace("evt_", "logevent_").replace("tel_", "")
    items = sorted(topics_with_alarms[topic])
    is_present_items = [f'isPresent("{item}")' for item in items]
    crit_items = [f'"{item}" == TRUE' for item in items]
    eval_items = [f'lambda: bool("{item}")' for item in items]
    as_items = [f"{item!r}" for item in items]
    monitored_values = [f'{item}={{{{ index .Fields "{item}" }}}}' for item in items]
    print(
        tick_script_template.format(
            topic=efd_topic,
            where=" AND ".join(is_present_items),
            crit=" OR ".join(crit_items),
            name=efd_topic,
            eval=", ".join(eval_items),
            as_str=", ".join(as_items),
            monitored_values=", ".join(monitored_values),
        )
    )
