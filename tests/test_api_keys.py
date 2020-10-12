import unittest
from tests import BaseTests
from atlasapi.atlas import Atlas
from pprint import pprint
from atlasapi.api_keys import ApiKey
from typing import Generator
KEY_ID = '5dd4d35fc56c98f31d6c454f'

class Test_API_keys(BaseTests):
    def test_00_raw_key_get(self):
        out = self.a.ApiKeys._get_api_keys()
        self.assertIsInstance(out,list)

    def test_01_keys_get(self):
        out = self.a.ApiKeys.all_keys
        pprint(type(out))
        self.assertIsInstance(out,Generator)
        for each_key in out:
            pprint(each_key.__dict__)

    def test_02_raw_key_get_one(self):
        out = self.a.ApiKeys._get_api_key(KEY_ID)
        self.assertIsInstance(out,dict)

    def test_03_key_get_one(self):
        out = self.a.ApiKeys.get_single_key(KEY_ID)
        self.assertTrue(out)

    def test_04_raw_get_whitelists(self):
        out = self.a.ApiKeys._get_whitelist_entry_for_key(key_id=KEY_ID)
        pprint(out)

if __name__ == '__main__':
    unittest.main()
