"""
Stupid and simple smoke tests.

Uses ENV vars to store user, key and group.

TODO: Create real tests


"""

from atlasapi.atlas import Atlas
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from json import dumps
from atlasapi.specs import AlertStatusSpec

from atlasapi.specs import DatabaseUsersPermissionsSpecs, RoleSpecs, DatabaseUsersUpdatePermissionsSpecs

USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER, API_KEY, GROUP_ID)


print('----------Test Get all closed alerts ------------------')

alert_list = []
for alert in a.Alerts.get_all_alerts(AlertStatusSpec.CLOSED, iterable=True):
    print(alert["id"])
    alert_list.append(alert["id"])

print('----------Test Get an alert ------------------')


details = a.Alerts.get_an_alert(alert_list[1])
pprint(details.__dict__)


print('----unack an alert-----')

details = a.Alerts.unacknowledge_an_alert(alert_list[1])

pprint(details)
