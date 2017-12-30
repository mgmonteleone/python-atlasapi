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
            "Get a Single Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s",
            "Create a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers",
            "Update a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s",
            "Delete a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers/admin/%s"
        },
        "Clusters" : {
            "Get a Single Cluster" : "/api/atlas/v1.0/groups/%s/clusters/%s"
        }
    }
    
    # Atlas enforced
    databaseName = "admin"
    
    # Requests
    requests_timeout = 2
    
    # HTTP Return code
    SUCCESS = 200
    CREATED = 201
