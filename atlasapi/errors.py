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

from .settings import Settings

class ErrRole(Exception):
    pass

class ErrPagination(Exception):
    def __init__(self):
        super().__init__("Issue occurs during the pagination.")
        
class ErrPaginationLimits(Exception):
    ERR_PAGE_NUM = 0
    ERR_ITEMS_PER_PAGE = 1
    
    def __init__(self, error_code):
        if error_code == ErrPaginationLimits.ERR_PAGE_NUM:
            super().__init__("pageNum can't be smaller than 1")
        elif error_code == ErrPaginationLimits.ERR_ITEMS_PER_PAGE:
            super().__init__("itemsPerPage can't be smaller than %d and greater than %d" % (Settings.itemsPerPageMin, Settings.itemsPerPageMax))
        else:
            super().__init__(str(error_code))
        
    def checkAndRaise(pageNum, itemsPerPage):
        """Check and Raise an Exception if needed
        
        Args:
            pageNum (int): Page number
            itemsPerPage (int): Number of items per Page
            
        Raises:
            ErrPaginationLimits. If we are out of limits
        
        """
        if pageNum < 1:
            raise ErrPaginationLimits(ErrPaginationLimits.ERR_PAGE_NUM)
        
        if itemsPerPage < Settings.itemsPerPageMin or itemsPerPage > Settings.itemsPerPageMax:
            raise ErrPaginationLimits(ErrPaginationLimits.ERR_ITEMS_PER_PAGE)

class ErrAtlasGeneric(Exception):
    def __init__(self, msg, c, details):
        super().__init__(msg)
        self.code = c
        self.details = details
        
    def getAtlasResponse(self):
        return self.code, self.details
    
class ErrAtlasBadRequest(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("Something was wrong with the client request.", c, details)

class ErrAtlasUnauthorized(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("Authentication is required", c, details)

class ErrAtlasForbidden(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("Access to the specified resource is not permitted.", c, details)

class ErrAtlasNotFound(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("The requested resource does not exist.", c, details)

class ErrAtlasMethodNotAllowed(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("The HTTP method is not supported for the specified resource.", c, details)

class ErrAtlasConflict(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("This is typically the response to a request to create or modify a property of an entity that is unique when an existing entity already exists with the same value for that property.", c, details)

class ErrAtlasServerErrors(ErrAtlasGeneric):
    def __init__(self, c, details):
        super().__init__("Something unexpected went wrong.", c, details)

class ErrConfirmationRequested(Exception):
    def __init__(self, msg):
        super().__init__(msg)
