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

from ipaddress import IPv4Address, IPv4Network
from pprint import pprint
from typing import Optional
import logging
from datetime import datetime
from isodate import parse_datetime
class WhitelistEntry(object):
    def __init__(self, cidrBlock: str = None, comment: str = None, ipAddress: str = None, links: list = None,
                 last_used: str = None, count: int = None, last_used_address: str = None):
        """
        For a single whitelist entry. Contains a bit of helper intelligence for ip addresses.

        :param cidrBlock:
        :param comment:
        :param ipAddress:
        :param links:
        """
        self.last_used_address: Optional[IPv4Address]  = None
        try:
            self.last_used_address = IPv4Address(last_used_address)
        except Exception:
            logging.warning('No last used address')

        self.count: Optional[int] = count
        self.last_used: Optional[datetime] = None
        try:
            self.last_used = parse_datetime(last_used)
        except Exception:
            logging.warning('Could not get last used date.')
        self.links = links
        self.ipAddress = ipAddress
        self.comment = comment
        self.cidrBlock = cidrBlock
        try:
            self.cidrBlockObj: IPv4Network = IPv4Network(self.cidrBlock)
        except Exception:
            self.cidrBlockObj = None
        try:
            self.ipAddressObj: IPv4Address = IPv4Address(self.ipAddress)
        except Exception:
            self.ipAddressObj = None

    @classmethod
    def fill_from_dict(cls, data_dict: dict):
        """
        Fills the object from the standard Atlas API dictionary.
        :param data_dict:
        :return:
        """
        cidrBlock = data_dict.get('cidrBlock', None)
        comment = data_dict.get('comment', None)
        ipAddress = data_dict.get('ipAddress', None)
        links = data_dict.get('links', None)
        last_used = data_dict.get('lastUsed', None)
        count = data_dict.get('count', 0)
        last_used_address = data_dict.get('lastUsedAddress', None)

        return cls(cidrBlock=cidrBlock, comment=comment, ipAddress=ipAddress, links=links,
                   last_used=last_used,count=count,last_used_address=last_used_address)

    def as_dict(self) -> dict:
        """
        Dumps obj as a json valid dict.
        :return:
        """
        orig_dict = self.__dict__
        orig_dict.__delitem__('ipAddressObj')
        orig_dict.__delitem__('cidrBlockObj')
        try:
            orig_dict['last_used_address'] = self.last_used_address.__str__()
        except Exception:
            pass
        return orig_dict
