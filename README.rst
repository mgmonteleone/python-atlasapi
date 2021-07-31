Atlas API
==========

Python Bindings for the Atlas Public API

This project intends to create a fairly opinionated set of bindings for the Atlas Public API which makes interacting
with Atlas using Python easier. The API makes extensive use of enums and other helper type objects to take some
of the guess work of administering Atlas clusters with Python.

In most cases objects will be returned based upon the structure of the json returned but the API Endpoints. These objects
are defined either in the `specs.py` module or in a module named after the objects themselves (`alerts.py` for example).


All calls to the Atlas API require API credentials, you can configure them in your Atlas project.


`Atlas API <https://docs.atlas.mongodb.com/api/>`__

`Configure Atlas API Access <https://docs.atlas.mongodb.com/configure-api-access/>`__

`Current state of the python-atlasapi support <https://github.com/mgmonteleone/python-atlasapi/blob/master/API.rst>`__


.. image:: https://img.shields.io/pypi/l/atlasapi.svg
     :target: https://pypi.org/project/atlasapi/

.. image:: https://img.shields.io/pypi/status/atlasapi.svg
     :target: https://pypi.org/project/atlasapi/

.. image:: https://img.shields.io/pypi/pyversions/atlasapi.svg
     :target: https://pypi.org/project/atlasapi/
     

Documentation
-------------
.. image:: https://readthedocs.org/projects/python-atlasapi/badge/?version=latest
     :target: https://python-atlasapi.readthedocs.io/en/latest/?badge=latest Found at https://python-atlasapi.readthedocs.io/

Found at https://python-atlasapi.readthedocs.io/

Autobuilt on each commit.

Installation
------------

This package is available for Python 3.6+.

.. image:: https://badge.fury.io/py/atlasapi.svg
     :target: https://pypi.org/project/atlasapi/


You can install the latest released version from pypi.

.. code:: bash

    pip3 install atlasapi




Usage
-----

Get All Database Users
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    # Low level Api
    details = a.DatabaseUsers.get_all_database_users(pageNum=1, itemsPerPage=100)
    
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

    details = a.DatabaseUsers.create_a_database_user(p)

Update a Database User
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    from atlasapi.specs import DatabaseUsersUpdatePermissionsSpecs, RoleSpecs

    a = Atlas("<user>","<password>","<groupid>")
    
    # Update roles and password
    p = DatabaseUsersUpdatePermissionsSpecs("password for test user")
    p.add_role("test-db", RoleSpecs.read, "a_collection")
    
    details = a.DatabaseUsers.update_a_database_user("test", p)

Delete a Database User
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    details = a.DatabaseUsers.delete_a_database_user("test")
    
Get a Single Database User
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python
    
    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    details = a.DatabaseUsers.get_a_single_database_user("test")

Clusters
^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    from atlasapi.clusters import  AdvancedOptions

    a = Atlas("<user>","<password>","<groupid>")
    
    # Is existing cluster ?
    a.Clusters.is_existing_cluster("cluster-dev")
    
    # Get All Clusters
    for cluster in a.Clusters.get_all_clusters(iterable=True):
        print(cluster["name"])
    
    # Get a Single Cluster
    details = a.Clusters.get_a_single_cluster("cluster-dev")
    
    # Delete a Cluster (dry run, raise ErrConfirmationRequested)
    details = a.Clusters.delete_a_cluster("cluster-dev")
    
    # Delete a Cluster (approved)
    details = a.Clusters.delete_a_cluster("cluster-dev", areYouSure=True)

    # Create a Simple Replica Set Cluster

    details = a.Clusters.create_basic_rs(name="cluster-dev")

    # Create a cluster

    provider_settings: ProviderSettings = ProviderSettings()
    regions_config = RegionConfig()
    replication_specs = ReplicationSpecs(regions_config={provider_settings.region_name: regions_config.__dict__})

    cluster_config = ClusterConfig(name='test2',
                               providerSettings=provider_settings,
                               replication_specs=replication_specs)

    output = a.Clusters.create_a_cluster(cluster_config)


    # Modify a cluster
    existing_config = a.Clusters.get_a_single_cluster_as_obj(cluster=TEST_CLUSTER_NAME)
    out.providerSettings.instance_size_name = InstanceSizeName.M10
    out.disk_size_gb = 13
    new_config = a.Clusters.modify_a_cluster('pyAtlasAPIClustersTest', out)
    pprint(new_config)

    # Modify cluster instance size

    a.Clusters.modify_cluster_instanct_size(cluster='pyAtlasAPIClustersTest',new_cluster_size=InstanceSizeName.M20)

    # Pause(unpause) a cluster

    a.Clusters.pause_cluster(cluster='pyAtlasAPIClustersTest', toggle_if_paused=True)


    # Get Advanced Options
    a.Clusters.get_single_cluster_advanced_options(cluster='pyAtlasAPIClustersTest')

    # Set Advanced Options
    options = AdvancedOptions(failIndexKeyTooLong=True)
    self.a.Clusters.modify_cluster_advanced_options(cluster='pyAtlasAPIClustersTest',
                                                                    advanced_options=options)

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
    details = a.Alerts.get_an_alert("597f221fdf9db113ce1755cd")
    
    # Acknowledge an Alert (BROKEN)
    #  until (now + 6 hours)
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    until = now + timedelta(hours=6)
    details = a.Alerts.acknowledge_an_alert("597f221fdf9db113ce1755cd", until, "Acknowledge reason")
    
    #  forever (BROKEN)
    details = a.Alerts.acknowledge_an_alert_forever("597f221fdf9db113ce1755cd", "Acknowledge reason")
    
    # Unacknowledge an Alert (BROKEN
    details = a.Alerts.unacknowledge_an_alert("597f221fdf9db113ce1755cd")



Metrics (Measurements)
^^^^^^^^^^^^^^^^^^^^^^
Examples coming soon.

Logs
^^^^^^^^^^^^^^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    from atlasapi.specs import AlertStatusSpec

    atlas = Atlas("<user>","<password>","<groupid>")

    atlas.Hosts.fill_host_list()
    test_host = atlas.Hosts.host_list[0]
    print(f'Will get a mongod log for {test_host.hostname}')
    out = atlas.Hosts.get_loglines_for_host(host_obj=test_host, log_name=AtlasLogNames.MONGODB)
    for each_line in out:
        print(each_line.__dict__)


Whitelists
^^^^^^^^^^
Examples coming soon.

Maintenance Windows
^^^^^^^^^^^^^^^^^^^

Examples coming soon.





Error Types
-----------

About ErrAtlasGeneric
^^^^^^^^^^^^^^^^^^^^^

All ErrAtlas* Exception class inherit from ErrAtlasGeneric.

.. code:: python
    
    try:
        ...
    except ErrAtlasGeneric as e:
        c, details = e.getAtlasResponse()
        
- 'c'
    HTTP return code (4xx or 5xx for an error, 2xx otherwise)
- 'details'
    Response payload

Exceptions
^^^^^^^^^^

- ErrRole
    A role is not compatible with Atlas
- ErrPagination
    An issue occurs during a "Get All" function with 'iterable=True'
- ErrPaginationLimits
    Out of limit on 'pageNum' or 'itemsPerPage' parameters
- ErrAtlasBadRequest
    Something was wrong with the client request.
- ErrAtlasUnauthorized
    Authentication is required
- ErrAtlasForbidden
    Access to the specified resource is not permitted.
- ErrAtlasNotFound
    The requested resource does not exist.
- ErrAtlasMethodNotAllowed
    The HTTP method is not supported for the specified resource.
- ErrAtlasConflict
    This is typically the response to a request to create or modify a property of an entity that is unique when an existing entity already exists with the same value for that property.
- ErrAtlasServerErrors
    Something unexpected went wrong.
- ErrConfirmationRequested
    Confirmation requested to execute the call.



Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues <https://github.com/mgmonteleone/python-atlasapi/issues>`__

Testing
-------

`Circle Ci <https://circleci.com/gh/mgmonteleone/python-atlasapi/>`__

develop

.. image:: https://circleci.com/gh/mgmonteleone/python-atlasapi/tree/develop.svg?style=svg&circle-token=34ce5f4745b141a0ee643bd212d85359c0594884
    :target: https://circleci.com/gh/mgmonteleone/python-atlasapi/tree/develop
    
master

.. image:: https://circleci.com/gh/mgmonteleone/python-atlasapi/tree/master.svg?style=svg&circle-token=34ce5f4745b141a0ee643bd212d85359c0594884
    :target: https://circleci.com/gh/mgmonteleone/python-atlasapi/tree/master

.. image:: https://readthedocs.org/projects/python-atlasapi/badge/?version=latest
     :target: https://python-atlasapi.readthedocs.io/en/latest/?badge=latest
       :alt: Documentation Status
