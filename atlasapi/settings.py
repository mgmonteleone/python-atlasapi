# Copyright (c) 2018 Yellow Pages Inc.
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

Provide few constants, APIs endpoint, ...
"""


class Settings:
    # Atlas APIs
    BASE_URL = 'https://cloud.mongodb.com'

    api_resources = {
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
            "Get the log file for a host in the cluster.": "/api/atlas/v1.0/groups/{GROUP-ID}/clusters/{"
                                                           "HOSTNAME}/logs/mongodb.gz"
        },
        "Events": {
            "Get All Project Events": "/api/atlas/v1.0/groups/{group_id}/events?pageNum={"
                                      "page_num}&itemsPerPage={items_per_page}"
        }

    }

    # Atlas enforced
    databaseName = "admin"

    # Atlas default pagination
    pageNum = 1
    itemsPerPage = 1000
    itemsPerPageMin = 1
    itemsPerPageMax = 2000

    # Requests
    requests_timeout = 10

    # HTTP Return code
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOTFOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    SERVER_ERRORS = 500
