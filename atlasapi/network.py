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
Network module

Permit to communicate with external APIs
"""

import requests
from requests.auth import HTTPDigestAuth
from .settings import Settings
from .errors import *
from pprint import pprint
import logging

logger = logging.getLogger('network')

logger.setLevel(logging.WARNING)

class Network:
    """Network constructor
    
    Args:
        user (str): user
        password (str): password
    """
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def answer(self, c, details):
        """Answer will provide all necessary feedback for the caller
        
        Args:
            c (int): HTTP Code
            details (dict): Response payload
        
        Returns:
            dict: Response payload
            
        Raises:
            ErrAtlasBadRequest
            ErrAtlasUnauthorized
            ErrAtlasForbidden
            ErrAtlasNotFound
            ErrAtlasMethodNotAllowed
            ErrAtlasConflict
            ErrAtlasServerErrors
        
        """
        if c in [Settings.SUCCESS, Settings.CREATED, Settings.ACCEPTED]:
            return details
        elif c == Settings.BAD_REQUEST:
            raise ErrAtlasBadRequest(c, details)
        elif c == Settings.UNAUTHORIZED:
            raise ErrAtlasUnauthorized(c, details)
        elif c == Settings.FORBIDDEN:
            raise ErrAtlasForbidden(c, details)
        elif c == Settings.NOTFOUND:
            raise ErrAtlasNotFound(c, details)
        elif c == Settings.METHOD_NOT_ALLOWED:
            raise ErrAtlasMethodNotAllowed(c, details)
        elif c == Settings.CONFLICT:
            raise ErrAtlasConflict(c, details)
        else:
            # Settings.SERVER_ERRORS
            raise ErrAtlasServerErrors(c, details)
    
    def get(self, uri):
        """Get request
        
        Args:
            uri (str): URI
            
        Returns:
            Json: API response
            
        Raises:
            Exception: Network issue
        """
        r = None
        
        try:
            r = requests.get(uri,
                             allow_redirects=True,
                             timeout=Settings.requests_timeout,
                             headers={},
                             auth=HTTPDigestAuth(self.user, self.password))
            return self.answer(r.status_code, r.json())

        except Exception:
            logger.warning('Request: {}'.format(r.request.__dict__))
            logger.warning('Response: {}'.format(r.__dict__))
            raise
        finally:
            if r:
                r.connection.close()
    
    def post(self, uri, payload):
        """Post request
        
        Args:
            uri (str): URI
            payload (dict): Content to post 
            
        Returns:
            Json: API response
            
        Raises:
            Exception: Network issue
        """
        r = None
        
        try:
            r = requests.post(uri,
                              json=payload,
                              allow_redirects=True,
                              timeout=Settings.requests_timeout,
                              headers={"Content-Type" : "application/json"},
                              auth=HTTPDigestAuth(self.user, self.password))
            return self.answer(r.status_code, r.json())
        except:
            raise
        finally:
            if r:
                r.connection.close()
    
    def patch(self, uri, payload):
        """Patch request
        
        Args:
            uri (str): URI
            payload (dict): Content to patch
            
        Returns:
            Json: API response
            
        Raises:
            Exception: Network issue
        """
        r = None
        
        try:
            r = requests.patch(uri,
                               json=payload,
                               allow_redirects=True,
                               timeout=Settings.requests_timeout,
                               headers={"Content-Type" : "application/json"},
                               auth=HTTPDigestAuth(self.user, self.password))
            return self.answer(r.status_code, r.json())
        except:
            raise
        finally:
            if r:
                r.connection.close()
    
    def delete(self, uri):
        """Delete request
        
        Args:
            uri (str): URI
            
        Returns:
            Json: API response
            
        Raises:
            Exception: Network issue
        """
        r = None
        
        try:
            r = requests.delete(uri,
                                allow_redirects=True,
                                timeout=Settings.requests_timeout,
                                headers={},
                                auth=HTTPDigestAuth(self.user, self.password))
            return self.answer(r.status_code, r.json())
        except:
            raise
        finally:
            if r:
                r.connection.close()
