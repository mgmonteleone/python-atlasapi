Atlas API
==========

A Python package for MongoDB Atlas Cloud provider.


`Atlas API <https://docs.atlas.mongodb.com/api/>`__

`Configure Atlas API Access <https://docs.atlas.mongodb.com/configure-api-access/>`__

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

Others
^^^^^^

.. code:: python

    from atlasapi.atlas import Atlas
    
    a = Atlas("<user>","<password>","<groupid>")
    
    # Is existing cluster ?
    a.Clusters.is_existing_cluster("cluster-dev")
    
    # Get a Single Cluster
    c, details = a.Clusters.get_a_single_cluster("cluster-dev")
    
    # Get a Single Database User
    c, details = a.DatabaseUser.get_a_single_database_user("test")

Error Types
-----------



Internal Notes
--------------



Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues <https://github.com/mickybart/python-atlasapi/issues>`__
