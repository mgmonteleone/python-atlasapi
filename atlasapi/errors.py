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

class ErrRoleException(Exception):
    pass

class ErrPaginationException(Exception):
    def __init__(self):
        super().__init__("Issue occurs during the pagination.")
        
class ErrPaginationLimitsException(Exception):
    ERR_PAGE_NUM = 0
    ERR_ITEMS_PER_PAGE = 1
    
    def __init__(self, error_code):
        if error_code == ErrPaginationLimitsException.ERR_PAGE_NUM:
            super().__init__("pageNum can't be smaller than 1")
        elif error_code == ErrPaginationLimitsException.ERR_ITEMS_PER_PAGE:
            super().__init__("itemsPerPage can't be smaller than %d and greater than %d" % (Settings.itemsPerPageMin, Settings.itemsPerPageMax))
        else:
            super().__init__(str(error_code))
        
    def checkAndRaise(pageNum, itemsPerPage):
        """Check and Raise an Exception if needed
        
        Args:
            pageNum (int): Page number
            itemsPerPage (int): Number of items per Page
            
        Raises:
            ErrPaginationLimitsException. If we are out of limits
        
        """
        if pageNum < 1:
            raise ErrPaginationLimitsException(ErrPaginationLimitsException.ERR_PAGE_NUM)
        
        if itemsPerPage < Settings.itemsPerPageMin or itemsPerPage > Settings.itemsPerPageMax:
            raise ErrPaginationLimitsException(ErrPaginationLimitsException.ERR_ITEMS_PER_PAGE)
