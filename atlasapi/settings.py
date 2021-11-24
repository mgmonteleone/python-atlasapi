# Copyright (c) 2021 Matthew G. Monteleone
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Settings module

Provides few constants, APIs endpoints.
"""
from os import getenv


class Settings:
    # Atlas APIs
    BASE_URL = getenv('BASE_URL','https://cloud.mongodb.com')
    URI_STUB = '/api/atlas/v1.0'

    api_resources = {
        "Project": {
            "Get One Project": URI_STUB + "/groups/{GROUP_ID}"
        },
        "Monitoring and Logs": {
            "Get all processes for group": "/api/atlas/v1.0/groups/{group_id}/processes?pageNum={"
                                           "page_num}&itemsPerPage={items_per_page}",
            "Get information for process in group": "/api/atlas/v1.0/groups/%s/processes/%s:&s?pageNum=%d"
                                                    "&itemsPerPage=%d",
            "Get measurement for host": "/api/atlas/v1.0/groups/{group_id}/processes/{host}:{"
                                        "port}/measurements?granularity={granularity}&period={period}&m={measurement}",
            "Get list of databases for host": "/api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{PORT}/databases",
            "Get measurements of database for host.": "/api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{"
                                                      "PORT}/databases/{DATABASE-NAME}/measurements",
            "Get list of disks or partitions for host.": "/api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{"
                                                         "PORT}/disks",
            "Get measurements of for host": "/api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{PORT}/disks/{"
                                            "DISK-NAME}/measurements",
            "Get the log file for a host in the cluster": "/api/atlas/v1.0/groups/{group_id}/clusters/{"
                                                          "host}/logs/{logname}"
        },
        "Events": {
            "Get All Project Events": URI_STUB + "/groups/{group_id}/events??includeRaw=true&pageNum={page_num}"
                                                 "&itemsPerPage={items_per_page}",
            "Get Project Events Since Date": URI_STUB + "/groups/{group_id}/events?includeRaw=true&pageNum={"
                                                        "page_num}&itemsPerPage={items_per_page}&minDate={"
                                                        "min_date}"
        },
        "Clusters": {
            "Get All Clusters": "/api/atlas/v1.0/groups/%s/clusters?pageNum=%d&itemsPerPage=%d",
            "Get a Single Cluster": "/api/atlas/v1.0/groups/%s/clusters/%s",
            "Delete a Cluster": "/api/atlas/v1.0/groups/%s/clusters/%s",
            "Create a Cluster": "/api/atlas/v1.0/groups/{GROUP_ID}/clusters/",
            "Modify a Cluster": "/api/atlas/v1.0/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}",
            "Test Failover": "/api/atlas/v1.0/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}/restartPrimaries",
            "Advanced Configuration Options": "/api/atlas/v1.0/groups/{GROUP_ID}/clusters/{"
                                              "CLUSTER_NAME}/processArgs",

        },
        "Database Users": {
            "Get All Database Users": "/api/atlas/v1.0/groups/%s/databaseUsers?pageNum=%d&itemsPerPage=%d",
            "Get a Single Database User": "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s",
            "Create a Database User": "/api/atlas/v1.0/groups/%s/databaseUsers",
            "Update a Database User": "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s",
            "Delete a Database User": "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s"
        },
        "Alerts": {
            "Get All Alerts": "/api/atlas/v1.0/groups/%s/alerts?pageNum=%d&itemsPerPage=%d",
            "Get All Alerts with status": "/api/atlas/v1.0/groups/%s/alerts?status=%s&pageNum=%d&itemsPerPage=%d",
            "Get an Alert": "/api/atlas/v1.0/groups/%s/alerts/%s",
            "Acknowledge an Alert": "/api/atlas/v1.0/groups/%s/alerts/%s"
        },
        "Whitelist": {
            "Get All Whitelist Entries": "/api/atlas/v1.0/groups/%s/whitelist?pageNum=%d&itemsPerPage=%d",
            "Get Whitelist Entry": "/api/atlas/v1.0/groups/%s/whitelist/%s",
            "Create Whitelist Entry": "/api/atlas/v1.0/groups/%s/whitelist",
            "Delete Whitelist Entry": "/api/atlas/v1.0/groups/%s/whitelist/%s"
        },
        "Maintenance Windows": {
            "Get Maintenance Window": "/api/atlas/v1.0/groups/{GROUP_ID}/maintenanceWindow",
            "Update Maintenance Window": "/api/atlas/v1.0/groups/{GROUP_ID}/maintenanceWindow",
            "Defer Maintenance Window": "/api/atlas/v1.0/groups/{GROUP_ID}/maintenanceWindow/defer",
            "Delete Maintenance Window": "/api/atlas/v1.0/groups/{GROUP_ID}/maintenanceWindow"
        },
        "Organization API Keys": {
            "Get all Organization API Keys associated with org": URI_STUB + "/orgs/{GROUP_ID}/apiKeys",
            "Get one Organization API Key": URI_STUB + "/orgs/{ORG_ID}/apiKeys/{API_KEY_ID}",
            "Get Whitelists for API Key": URI_STUB + "/orgs/{ORG_ID}/apiKeys/{API_KEY_ID}/whitelist",
            "Create one or more whitelist entries for APi Key": URI_STUB + "/orgs/{GROUP_ID}/apiKeys/{"
                                                                           "API_KEY_ID}/whitelist",
            "Get a single whitelist entry": URI_STUB + "/orgs/{GROUP_ID}/apiKeys/{API_KEY_ID}/whitelist/{IP_ADDRESS}"
            # Incomplete
        },
        "Project API Keys": {
            "Get All API Keys Assigned to Project": URI_STUB + "/groups/{GROUP_ID}/apiKeys",

        },
        "Cloud Backup": {
            "Get all Cloud Backups for cluster": URI_STUB + "/groups/{GROUP_ID}/clusters/"
                                                            "{CLUSTER_NAME}/backup/snapshots",
            "Get snapshot by SNAPSHOT-ID": URI_STUB + "/groups/{GROUP_ID}/clusters/"
                                                      "{CLUSTER_NAME}/backup/snapshots/{SNAPSHOT_ID}",
            "Delete snapshot by SNAPSHOT-ID": URI_STUB + "/groups/{GROUP_ID}/clusters/"
                                                         "{CLUSTER_NAME}/backup/snapshots/{SNAPSHOT_ID}",
            "Take an on-demand snapshot": URI_STUB + "/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}/backup/snapshots",

        },
        "Cloud Backup Restore Jobs": {
            "Get all Cloud Backup restore jobs by cluster": URI_STUB + "/groups/{GROUP_ID}/clusters/"
                                                                       "{CLUSTER_NAME}/backup/restoreJobs",
            "Get Cloud Backup restore job by cluster": URI_STUB + "/groups/{GROUP_ID}/clusters/"
                                                                  "{CLUSTER_NAME}/backup/restoreJobs/{JOB_ID}",
            "Restore snapshot by cluster": URI_STUB + "/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}"
                                                       "/backup/restoreJobs",
            "Cancel manual download restore job by job_id": URI_STUB + "/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}"
                                                                         "/backup/restoreJobs/{JOB_ID}"

        }

    }
    #

    # Atlas enforced
    databaseName = "admin"

    # Atlas default pagination
    pageNum = 1
    itemsPerPage = 1000
    itemsPerPageMin = 1
    itemsPerPageMax = 2000

    # Requests
    requests_timeout = 10
    file_request_timeout = 360

    # HTTP Return code
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOTFOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    SERVER_ERRORS = 500
