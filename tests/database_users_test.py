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
from atlasapi.errors import ErrAtlasNotFound

from atlasapi.specs import DatabaseUsersPermissionsSpecs, RoleSpecs, DatabaseUsersUpdatePermissionsSpecs

USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER, API_KEY, GROUP_ID)


print('----------Test Get all Users ------------------')
details = a.DatabaseUsers.get_all_database_users(pageNum=1, itemsPerPage=100)
pprint(details)

print('----------Test Get all Users (iterable) ------------------')

for user in a.DatabaseUsers.get_all_database_users(iterable=True):
    print(user["username"])

print('----------Test Adding a User------------------')

p = DatabaseUsersPermissionsSpecs("testuser3", "not_a_password")
p.add_roles("test-db",
            [RoleSpecs.dbAdmin,
            RoleSpecs.readWrite])

p.add_role("other-test-db", RoleSpecs.readWrite, "a_collection")

details = a.DatabaseUsers.create_a_database_user(p)

pprint(details)

#print('---------Modify a User---------------')
#
## Update roles and password
#p = DatabaseUsersUpdatePermissionsSpecs("new_password")
#p.add_role("test-db", RoleSpecs.read, "b_collection")
#
#details = a.DatabaseUsers.update_a_database_user("testuser", p)
#
#pprint(details)
#
#
print('----------Delete A Database User -----------------')

try:
    details = a.DatabaseUsers.delete_a_database_user("testuser3")
    pprint(details)
except ErrAtlasNotFound as e:
    pprint('The user was not found {}'.format(e))

