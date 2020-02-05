# Copyright (c) 2019 Matthew G. Monteleone
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

Module which handles the basic network operations with the Atlas API>
"""

import requests
from requests.auth import HTTPDigestAuth
from .settings import Settings
from .errors import *
import logging
from json import dumps
from io import BytesIO
from typing import Union
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

    def answer(self, c, details: Union[dict,BytesIO]):
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
        if c in [Settings.SUCCESS, Settings.CREATED, Settings.ACCEPTED, Settings.NO_CONTENT]:
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

    def get_file(self, uri):
        """Get request which returns a binary file

        Args:
            uri (str): URI

        Returns:
            Binary File: API response as file

        Raises:
            Exception: Network issue
        """
        r = None

        try:
            file_obj = BytesIO()
            r = requests.get(uri,
                             allow_redirects=False,
                             stream = True,
                             timeout=Settings.file_request_timeout,
                             headers={},
                             auth=HTTPDigestAuth(self.user, self.password))
            logger.debug("Auth information = {} {}".format(self.user, self.password))

            for chunk in r.iter_content(chunk_size=1024):
                # writing one chunk at a time to  file
                if chunk:
                    logger.warning("Writing 1 Kbyte chunk to the file like object")
                    file_obj.write(chunk)
            logger.info("---- Completed downloading the file. ----")
            return self.answer(r.status_code, file_obj)

        except Exception:
            logger.warning('Request: {}'.format(r.request.__dict__))
            logger.warning('Response: {}'.format(r.__dict__))
            raise
        finally:
            if r:
                r.connection.close()


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
            logger.debug("Auth information = {} {}".format(self.user, self.password))

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

            try:
                output = r.json()
            except:
                logger.warning("PATCH doesnt return data!")
                output = {}

            return self.answer(r.status_code, output)
        except Exception as e:

            raise e
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
            return self.answer(r.status_code, {"deleted": True})
        except Exception as e:
            raise e
        finally:
            if r:
                r.connection.close()
