import requests
from requests.auth import HTTPDigestAuth
from settings import Settings

class Network:
    def __init__(self, user, password):
        """Network constructor
        
        Args:
            user (str): user
            password (str): password
        
        """
        self.user = user
        self.password = password
    
    def get(self, uri):
        """Get
        
        Args:
            uri (str): URI
            
        Returns:
            Int, Json. HTTP code and API response
            
        Raises:
            Exception. Network issue
        """
        r = None
        
        try:
            r = requests.get(uri,
                             allow_redirects=True,
                             timeout=Settings.requests_timeout,
                             headers={},
                             auth=HTTPDigestAuth(self.user, self.password))
            return (r.status_code, r.json())
        except:
            raise
        finally:
            if r:
                r.connection.close()
    
    def post(self, uri, payload):
        """Post
        
        Args:
            uri (str): URI
            payload (dict): Content to post 
            
        Returns:
            Int, Json. HTTP code and API response
            
        Raises:
            Exception. Network issue
        """
        r = None
        
        try:
            r = requests.post(uri,
                              json=payload,
                              allow_redirects=True,
                              timeout=Settings.requests_timeout,
                              headers={"Content-Type" : "application/json"},
                              auth=HTTPDigestAuth(self.user, self.password))
            return (r.status_code, r.json())
        except:
            raise
        finally:
            if r:
                r.connection.close()
                
    def delete(self, uri):
        """Delete
        
        Args:
            uri (str): URI
            
        Returns:
            Int, Json. HTTP code and API response
            
        Raises:
            Exception. Network issue
        """
        r = None
        
        try:
            r = requests.delete(uri,
                                allow_redirects=True,
                                timeout=Settings.requests_timeout,
                                headers={},
                                auth=HTTPDigestAuth(self.user, self.password))
            return (r.status_code, r.json())
        except:
            raise
        finally:
            if r:
                r.connection.close()
