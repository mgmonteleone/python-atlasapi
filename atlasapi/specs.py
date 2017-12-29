from settings import Settings

class RoleSpecs:
    """Roles supported by Atlas"""
    dbAdmin = "dbAdmin"
    readWrite = "readWrite"
    read = "read"

class DatabaseUsersPermissionsSpecs:
    """Permissions spec for Database User"""
    
    def __init__(self, username, password, databaseName=Settings.databaseName):
        """Constructor
        
        Args:
            username (str): Username of the DB
            password (str): Password for the username
            
        Kwargs:
            databaseName (str): Auth Database Name
        """
        self.username = username
        self.password = password
        self.databaseName = databaseName
        self.roles=[]
    
    def getSpecs(self):
        """Get specs
        
        Returns:
            dict. Representation of the object
        """
        content = {
            "databaseName" : self.databaseName,
            "roles" : self.roles,
            "username" : self.username,
            "password" : self.password
        }
        
        return content
    
    def add_roles(self, databaseName, roleNames):
        """Add multiple roles
        
        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles
        """
        for roleName in roleNames:
            self.add_role(databaseName, roleName)
    
    def add_role(self, databaseName, roleName):
        """Add one role
        
        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role
        """
        role = {"databaseName" : databaseName,
                "roleName" : roleName}
        
        if role not in self.roles:
            self.roles.append(role)

    def remove_roles(self, databaseName, roleNames):
        """Remove multiple roles
        
        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles
        """
        for roleName in roleNames:
            self.remove_role(databaseName, roleName)
            
    def remove_role(self, databaseName, roleName):
        """Remove one role
        
        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role
        """
        role = {"databaseName" : databaseName,
                  "roleName" : roleName}
        
        if role in self.roles:
            self.roles.remove(role)
        
    def clear_roles(self):
        self.roles.clear()
