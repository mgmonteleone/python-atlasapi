Atlas API
==========

A Python package for MongoDB Atlas Cloud provider.


`Atlas API <https://docs.atlas.mongodb.com/api/>`__

`Configure Atlas API Access <https://docs.atlas.mongodb.com/configure-api-access/>`__

`Current state of the python-atlasapi support <https://github.com/mickybart/python-atlasapi/blob/master/API.rst>`__

Installation
------------

This package is available for Python 3.5+.

.. code:: bash

    pip3 install atlasapi

Or install the development version from github:

.. code:: bash

    pip3 install git+https://github.com/mickybart/python-atlasapi.git

Usage
-----

Get All Database Users
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    # Low level Api
    c, details = a.DatabaseUsers.get_all_database_users(pageNum=1, itemsPerPage=100)
    
    # Iterable
    for user in a.DatabaseUsers.get_all_database_users(iterable=True):
        print(user["username"])

Create a Database User
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    from atlasapi.specs import DatabaseUsersPermissionsSpecs, RoleSpecs

    a = Atlas("<user>","<password>","<groupid>")

    p = DatabaseUsersPermissionsSpecs("test", "password for test user")
    p.add_roles("test-db",
                [RoleSpecs.dbAdmin,
                RoleSpecs.readWrite])
    p.add_role("other-test-db", RoleSpecs.readWrite, "a_collection")

    c, details = a.DatabaseUsers.create_a_database_user(p)
    a.isCreated(c)

Update a Database User
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    from atlasapi.specs import DatabaseUsersUpdatePermissionsSpecs, RoleSpecs

    a = Atlas("<user>","<password>","<groupid>")
    
    # Update roles and password
    p = DatabaseUsersUpdatePermissionsSpecs("password for test user")
    p.add_role("test-db", RoleSpecs.read, "a_collection")
    
    c, details = a.DatabaseUsers.update_a_database_user("test", p)
    a.isSuccess(c)

Delete a Database User
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    c, details = a.DatabaseUsers.delete_a_database_user("test")
    a.isSuccess(c)
    
Get a Single Database User
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python
    
    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    c, details = a.DatabaseUser.get_a_single_database_user("test")
    a.isSuccess(c)

Projects
^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    # Get All Projects
    for project in a.Projects.get_all_projects(iterable=True):
        print(project["name"])
        
    # Get One Project
    c, details = a.Projects.get_one_project("59a03f423b34b9132757aa0d")
    
    # Create a Project
    c, details = a.Projects.create_a_project("test", "599eed989f78f769464d28cc")
    a.isCreated(c)

Clusters
^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    # Is existing cluster ?
    a.Clusters.is_existing_cluster("cluster-dev")
    
    # Get All Clusters
    for cluster in a.Clusters.get_all_clusters(iterable=True):
        print(cluster["name"])
    
    # Get a Single Cluster
    c, details = a.Clusters.get_a_single_cluster("cluster-dev")
    
    # Delete a Cluster (dry run)
    c, details = a.Clusters.delete_a_cluster("cluster-dev")
    
    # Delete a Cluster (approved)
    c, details = a.Clusters.delete_a_cluster("cluster-dev", areYouSure=True)
    a.isAccepted(c)

Alerts
^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    from atlasapi.specs import AlertStatusSpec
    
    a = Atlas("<user>","<password>","<groupid>")
    
    # Get All Alerts in OPEN status
    for alert in a.Alerts.get_all_alerts(AlertStatusSpec.OPEN, iterable=True):
        print(alert["id"])
    
    # Get an Alert
    c, details = a.Alerts.get_an_alert("597f221fdf9db113ce1755cd")
    
    # Acknowledge an Alert
    #  until (now + 6 hours)
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    until = now + timedelta(hours=6)
    c, details = a.Alerts.acknowledge_an_alert("597f221fdf9db113ce1755cd", until, "Acknowledge reason")
    
    #  forever
    c, details = a.Alerts.acknowledge_an_alert_forever("597f221fdf9db113ce1755cd", "Acknowledge reason")
    
    # Unacknowledge an Alert
    c, details = a.Alerts.unacknowledge_an_alert("597f221fdf9db113ce1755cd")

Error Types
-----------



Internal Notes
--------------



Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues <https://github.com/mickybart/python-atlasapi/issues>`__
