class Settings:
    # Atlas APIs
    BASE_URL = 'https://cloud.mongodb.com'
    
    api_resources = {
        "Database Users" : {
            "Create a Database User" : "/api/atlas/v1.0/groups/%s/databaseUsers",
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
