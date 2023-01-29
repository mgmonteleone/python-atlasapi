# Copyright (c) 2022 Matthew G. Monteleone
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

from math import ceil
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from atlasapi.settings import Settings
from atlasapi.errors import *
import logging
from json import dumps
from io import BytesIO
from typing import Union

logger = logging.getLogger('network')
logger.setLevel(logging.WARNING)


def merge(dict1, dict2):
    return dict2.update(dict1)


class Network:
    """Network constructor
    
    Args:
        user (str): user
        password (str): password
    """

    def __init__(self, key, secret, AuthMethod: Union[HTTPDigestAuth, HTTPBasicAuth] = HTTPDigestAuth):
        self.key: str = key
        self.secret: str = secret
        self.auth_method: Union[HTTPDigestAuth, HTTPBasicAuth] = AuthMethod

    def answer(self, c, details: Union[dict, BytesIO]):
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

    # noinspection PyArgumentList
    def get_file(self, uri, **kwargs):
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
                             stream=True,
                             timeout=Settings.file_request_timeout,
                             headers={},
                             auth=self.auth_method(self.key, self.secret),
                             **kwargs)
            logger.debug("Auth information = {} {}".format(self.key, self.secret))
            if kwargs is not None:
                logger.info(f"kwargs are: {kwargs}")

            for chunk in r.iter_content(chunk_size=1024):
                # writing one chunk at a time to  file
                if chunk:
                    logger.debug("Writing 1 Kbyte chunk to the file like object")
                    file_obj.write(chunk)
            logger.info("---- Completed downloading the file. ----")
            return self.answer(r.status_code, file_obj)

        except Exception as e:
            try:
                logger.warning('Request: {}'.format(r.request.__dict__))
                logger.warning('Response: {}'.format(r.__dict__))
                raise e
            except AttributeError:
                raise e
        finally:
            if r:
                r.connection.close()

    def _paginate(self, method , url, **kwargs):
        """(Internal) Paginate requests
        
        Args:
            method (str): method for the Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.
            url (str): URL for the Request object

        Yields:
            dict: Response payload
        """
        session = None

        try:
            logger.debug(f"{method} - URI Being called is {url}")
            session = requests.Session()
            request = session.request(method=method, url=url, **kwargs)
            logger.debug("Request arguments: {}".format(str(kwargs)))
            first_page = self.answer(request.status_code, request.json())
            yield first_page
            total_count = first_page.get("totalCount", 0)
            items_per_page = Settings.itemsPerPage
            if total_count > items_per_page:
                logger.warning(f"More than on page required, proceeding . . .")
                for page_number in range(2, ceil(total_count / items_per_page) + 1):
                    # Need to ensure that any params sent in kwargs are merged with the pageNum param.
                    if kwargs.get('params'):
                        existing_params: dict = kwargs.get('params')
                        logger.debug(f"Existing params are: {existing_params}")
                        existing_params.update(dict(pageNum=page_number))
                        logger.debug(f"New params are {existing_params}")
                        kwargs["params"] = existing_params
                        logger.debug(f"Fully updated kwargs is now... {kwargs}")
                    request = session.request(method=method, url=url, **kwargs)
                    logger.debug("Request arguments: {}".format(str(kwargs)))
                    next_page = self.answer(request.status_code, request.json())
                    yield next_page
        finally:
            if session:
                session.close()

    def get(self, uri, **kwargs):
        """Get request

        Args:
            call_params:
            uri (str): URI

        Returns:
            Json: API response

        Raises:
            Exception: Network issue
        """
        if kwargs is not None:
            logger.info(f"kwargs are: {kwargs}")
        yield from self._paginate(
                method='GET',
                url=uri,
                allow_redirects=True,
                timeout=Settings.requests_timeout,
                headers={},
                auth=self.auth_method(self.key, self.secret),
                **kwargs)

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
                              headers={"Content-Type": "application/json"},
                              auth=self.auth_method(self.key, self.secret))
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
                               headers={"Content-Type": "application/json"},
                               auth=self.auth_method(self.key, self.secret))
            logger.info(f'THe Payload is.... {payload}')
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
                                auth=self.auth_method(self.key, self.secret))
            return self.answer(r.status_code, {"deleted": True})
        except Exception as e:
            raise e
        finally:
            if r:
                r.connection.close()
