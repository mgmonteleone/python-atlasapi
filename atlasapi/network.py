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

import requests
from requests.auth import HTTPDigestAuth
from .settings import Settings

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
    
    def patch(self, uri, payload):
        """Patch
        
        Args:
            uri (str): URI
            payload (dict): Content to patch
            
        Returns:
            Int, Json. HTTP code and API response
            
        Raises:
            Exception. Network issue
        """
        r = None
        
        try:
            r = requests.patch(uri,
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
