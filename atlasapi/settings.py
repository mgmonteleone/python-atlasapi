"""
Copyright (c) 2017 Yellow Pages Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

class Settings:
    # Atlas APIs
    BASE_URL = 'https://cloud.mongodb.com'
    
    api_resources = {
        "Database Users" : {
            "Get All Database Users" : "/api/atlas/v1.0/groups/%s/databaseUsers?pageNum=%d&itemsPerPage=%d",
            "Get a Single Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s",
            "Create a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers",
            "Update a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s",
            "Delete a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s"
        },
        "Projects" : {
            "Get All Projects" : "/api/atlas/v1.0/groups?pageNum=%d&itemsPerPage=%d",
            "Get One Project" : "/api/atlas/v1.0/groups/%s",
            "Create a Project" : "/api/atlas/v1.0/groups"
        },
        "Clusters" : {
            "Get All Clusters" : "/api/atlas/v1.0/groups/%s/clusters?pageNum=%d&itemsPerPage=%d",
            "Get a Single Cluster" : "/api/atlas/v1.0/groups/%s/clusters/%s",
            "Delete a Cluster" : "/api/atlas/v1.0/groups/%s/clusters/%s"
        },
        "Alerts" : {
            "Get All Alerts" : "/api/atlas/v1.0/groups/%s/alerts?pageNum=%d&itemsPerPage=%d",
            "Get All Alerts with status" : "/api/atlas/v1.0/groups/%s/alerts?status=%s&pageNum=%d&itemsPerPage=%d",
            "Get an Alert" : "/api/atlas/v1.0/groups/%s/alerts/%s",
            "Acknowledge an Alert" : "/api/atlas/v1.0/groups/%s/alerts/%s"
        }
    }
    
    # Atlas enforced
    databaseName = "admin"
    
    # Atlas default pagination
    pageNum = 1
    itemsPerPage = 100
    itemsPerPageMin = 1
    itemsPerPageMax = 100
    
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
