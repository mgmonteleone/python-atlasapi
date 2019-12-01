# Copyright (c) 2019 Joe Drumgoole
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
# Modifications copyright (C) Joe Drumgoole

import argparse
import sys
import pprint
import logging
import os

from atlasapi.atlas import Atlas

def main(args):
    """

    :param args: Expect sys.argv
    :return: None
    """
    parser = argparse.ArgumentParser(
         prog="atlascli",
         description="A command line interface too the MongoDB Atlas"
                     "database as a service."
                     "https://www.mongodb.com/cloud/atlas for more info"
                     "See also https://docs.atlas.mongodb.com/configure-api-access/#programmatic-api-keys"
                     "For how to obtain a programmatic API key required to access the API"
         )


    parser.add_argument("--publickey", help="MongoDB Atlas public API key")
    parser.add_argument("--privatekey", help="MongoDB Atlas private API key")
    parser.add_argument("--atlasgroup", help="Default group (aka project)")

    parser.add_argument("--debug", default=False, action="store_true",
                        help="Turn on logging at debug level")
    args = parser.parse_args(args)

    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    logging.debug("logging is on at DEBUG level")

    if args.publickey:
        public_key = args.publickey
    else:
        public_key = os.getenv("ATLAS_PUBLIC_KEY")
        if public_key is None:
            print( "you must specify an ATLAS public key via --publickey arg "
                   "or the environment variable ATLAS_PUBLIC_KEY")
            sys.exit(1)

    if args.privatekey:
        private_key = args.privatekey
    else:
        private_key = os.getenv("ATLAS_PRIVATE_KEY")
        if private_key is None:
            print( "you must specify an an ATLAS private key via --privatekey"
                   "arg or the environment variable ATLAS_PRIVATE_KEY")
            sys.exit(1)

    atlas = Atlas(public_key, private_key, args.atlasgroup)

    print("List Clusters:")
    for i in atlas.Clusters.get_all_clusters(iterable=True):
        pprint.pprint(i)


if __name__ == "__main__":
    main(sys.argv)
