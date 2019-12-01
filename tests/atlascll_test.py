import unittest
import os
import sys

from atlascli.cli import main


class AtlascliTest(unittest.TestCase):

    def test_atlascli(self):
        atlas_public_key = os.getenv("ATLAS_PUBLIC_KEY")
        self.assertTrue(atlas_public_key)
        atlas_private_key = os.getenv("ATLAS_PRIVATE_KEY")
        self.assertTrue(atlas_private_key)
        atlas_group = os.getenv("ATLAS_GROUP")
        self.assertTrue(atlas_group)

        main(["--publickey", atlas_public_key,
              "--privatekey", atlas_private_key,
              "--atlasgroup", atlas_group,
              "--list",
              ])

        main(["--publickey", atlas_public_key,
              "--privatekey", atlas_private_key,
              "--atlasgroup", atlas_group,
              "--list",
              "--format", "full",
              ])

        main(["--publickey", atlas_public_key,
              "--privatekey", atlas_private_key,
              "--atlasgroup", atlas_group,
              "--list",
              "--format", "short",
              ])
if __name__ == '__main__':
    unittest.main()
