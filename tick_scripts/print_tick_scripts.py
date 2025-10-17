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
var message = '{{ if eq .Level "OK" }}Summit EFD HVAC {name} is back to normal.{{ else }}Summit EFD HVAC
{name} alarm. <PUT SLACK USER IDS HERE> please check.
{{ end }}'
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
        .stateChangesOnly()
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
    print(
        tick_script_template.format(
            topic=efd_topic,
            where=" AND ".join(is_present_items),
            crit=" OR ".join(crit_items),
            name=efd_topic,
            eval=", ".join(eval_items),
            as_str=", ".join(as_items),
        )
    )
