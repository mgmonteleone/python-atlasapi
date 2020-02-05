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
# import pprint
import logging
import os
from enum import Enum

from atlasapi.atlas import Atlas

from atlascli.listcommand import ListCommand, ListFormat


class AtlasResource(Enum):
    ORGANIZATION = "organization"
    PROJECT = "project"
    CLUSTER = "cluster"

    def __str__(self):
        return self.value


def main(args):
    """

    :param args: Expect sys.argv
    :return: None
    """
    parser = argparse.ArgumentParser(prog="atlascli",
                                     description="A command line interface to the MongoDB Atlas"
                                                 "database as a service."
                                                 "https://www.mongodb.com/cloud/atlas for more info"
                                                 "See also https://docs.atlas.mongodb.com/configure-api-access"
                                                 "/#programmatic-api-keys "
                                                 "For how to obtain a programmatic API key required to access the API"
                                     )

    parser.add_argument("--publickey", help="MongoDB Atlas public API key")
    parser.add_argument("--privatekey", help="MongoDB Atlas private API key")
    parser.add_argument("--atlasgroup", help="Default group (aka project)")

    parser.add_argument("--format", type=ListFormat,
                        choices=list(ListFormat),
                        default=ListFormat.short,
                        help="Format for output of list command [default: %(default)s]")

    parser.add_argument("--resource",
                        type=AtlasResource, default=AtlasResource.CLUSTER,
                        choices=list(AtlasResource),
                        help="Which resource type are we operating on:"
                             "organization, project or cluster? [default: %(default)s]")

    parser.add_argument('--id', type=str, help='Specify a resource id')

    parser.add_argument("--debug", default=False, action="store_true",
                        help="Turn on logging at debug level [default: %(default)s]")

    parser.add_argument("--list", default=False, action="store_true",
                        help="List a set of resources [default: %(default)s]")

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
            print("you must specify an ATLAS public key via --publickey arg "
                  "or the environment variable ATLAS_PUBLIC_KEY")
            sys.exit(1)

    if args.privatekey:
        private_key = args.privatekey
    else:
        private_key = os.getenv("ATLAS_PRIVATE_KEY")
        if private_key is None:
            print("you must specify an an ATLAS private key via --privatekey"
                  "arg or the environment variable ATLAS_PRIVATE_KEY")
            sys.exit(1)

    atlas = Atlas(public_key, private_key, args.atlasgroup)

    if args.list:
        if args.resource == AtlasResource.CLUSTER:
            list_cmd = ListCommand(args.format)
            if args.id:
                print("Cluster:")
                cluster = atlas.Clusters.get_single_cluster(cluster=args.id)
                list_cmd.list_one(cluster)
            else:
                print("Cluster list:")
                clusters = atlas.Clusters.get_all_clusters(iterable=True)
                total = list_cmd.list_all(clusters)
                print(f"{total} cluster(s)")


if __name__ == "__main__":
    main(sys.argv[1:])  # strip off the program name
