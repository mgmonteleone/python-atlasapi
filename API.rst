Atlas API Support
=================

Status about API implementation

Database Users
--------------

Status : [100%] :heavy_check_mark:

- Get All Database Users :ballot_box_with_check:
- Get a Single Database User :ballot_box_with_check:
- Create a Database User :ballot_box_with_check:
- Update a Database User :ballot_box_with_check:
- Delete a Database User :ballot_box_with_check:




Custom MongoDB Roles
---------------------

Status : [0%]

- Get all custom MongoDB roles in the project.
- Get the custom MongoDB role named {ROLE-NAME}.
- Create a new custom MongoDB role in the project.
- Update a custom MongoDB role in the project.
- Delete a custom MongoDB role from the project.

Projects
--------

Status : [100%]

- Get All Projects :ballot_box_with_check:
- Get One Project :ballot_box_with_check:
- Create a Project :ballot_box_with_check:

Clusters
--------

Status : [100%]

- Get All Clusters :ballot_box_with_check:
- Get a Single Cluster :ballot_box_with_check:
- Create a Cluster :ballot_box_with_check:
- Modify a Cluster :ballot_box_with_check:
- Delete a Cluster :ballot_box_with_check:
- Get Advanced Configuration Options for One Cluster :ballot_box_with_check:
- Modify Advanced Configuration Options for One Cluster :ballot_box_with_check:
- Test Failover :ballot_box_with_check:

- (Helper) Modify cluster instance size :ballot_box_with_check:
- (Helper) Pause/Unpause Cluster :ballot_box_with_check:

Alerts
------

Status : [50%]

- Get All Alerts :ballot_box_with_check:
- Get an Alert :ballot_box_with_check:
- Acknowledge an Alert (include Unacknowledge) (BROKEN)

Alert Configurations
--------------------

Status : [0%]

VPC
---

Status : [0%]

Monitoring and Logs
-------------------

Processes
+++++++++

- Get all processes for the specified group. [Completed]
- Get information for the specified process in the specified group.


Hosts
+++++

- Get measurements for the specified host.
- Get logfile for the specified host.
- Get Loglines for the specified host.

Databases
+++++++++

- Get the list of databases for the specified host.
- Get measurements of the specified database for the specified host.

Disks
+++++

- Get the list of disks or partitions for the specified host.
- Get measurements of specified disk for the specified host.


Logs
++++

Status : [50%]


- Get the log file for a host in the cluster. :ballot_box_with_check:
- Get loglines for a host in the cluster. :ballot_box_with_check:
- Get log files for all hosts in a cluster (#24)
- Get log files for all hosts in a project (#25) :ballot_box_with_check:


IP Whitelist
------------

Status : [80%]

- Get All Entries
- Add a single entry
- Delete a entry
- update a entry(missing)

Events
++++++

Status: [50%]

- Get All Organization Events
- Get One Organization Event
- Get All Project Events
- Ge One Project Event

Organizations
--------------

Status: [0%]


Maintenance Windows
--------------------

Status: [60%]

- Get Maintenance Window Settings :ballot_box_with_check:
- Update Maintenance Window Settings :ballot_box_with_check:
- Defer Maintenance for one week :ballot_box_with_check:
- Commence Maintenance ASAP
- Clear Maintenance Window