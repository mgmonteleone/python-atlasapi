import requests
from settings import Settings
from network import Network

class Atlas:
    def __init__(self, user, password, group):
        """Atlas constructor
        
        Args:
            user (str): Atlas user
            password (str): Atlas password
            group (str): Atlas group
        """
        
        self.group = group
        
        # Network calls which will handld user/passord for auth
        self.network = Network(user, password)
        
        # APIs
        self.Clusters = Atlas._Clusters(self)
        self.DatabaseUsers = Atlas._DatabaseUsers(self)
    
    def isSuccess(self, code):
        return (code == Settings.SUCCESS)
    
    def isCreated(self, code):
        return (code == Settings.CREATED)
        
    class _Clusters:
        """Clusters API
        
        see: https://docs.atlas.mongodb.com/reference/api/clusters/
        """
        
        def __init__(self, atlas):
            """_Cluster constructor
            
            Args:
                atlas (Atlas): Atlas instance
            """
            self.atlas = atlas
            
        def is_existing_cluster(self, cluster):
            """Check if the cluster exists
            
            Not part of Atlas api but provided to simplify some code
            
            Args:
                cluster (str): The cluster name
            """
            
            code, content = self.get_a_single_cluster(cluster)
            return self.atlas.isSuccess(code)
        
        def get_a_single_cluster(self, cluster):
            """Get a Single Cluster
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/
            
            Args:
                cluster (str): The cluster name
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"] % (self.atlas.group, cluster)
            return self.atlas.network.get(Settings.BASE_URL + uri)
            
    class _DatabaseUsers:
        """Database Users API
        
        see: https://docs.atlas.mongodb.com/reference/api/database-users/
        """
        
        def __init__(self, atlas):
            """_DatabaseUsers constructor
            
            Args:
                atlas (Atlas): Atlas instance
            """
            self.atlas = atlas
        
        def create_a_database_user(self, permissions):
            """Create a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-create-a-user/
            
            Args:
                permissions (DatabaseUsersPermissionsSpec): Permissions to apply
            """
            uri = Settings.api_resources["Database Users"]["Create a Database User"] % self.atlas.group
            return self.atlas.network.post(Settings.BASE_URL + uri, permissions.getSpecs())
        
        def delete_a_database_user(self, user):
            """Delete a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-delete-a-user/
            
            Args:
                user (str): User to delete
            """
            uri = Settings.api_resources["Database Users"]["Delete a Database User"] % (self.atlas.group, user)
            return self.atlas.network.delete(Settings.BASE_URL + uri)
