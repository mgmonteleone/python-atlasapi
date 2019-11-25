atlascli - A Command line program for MongoDB Atlas
====================================================

The command line help for atlascli.py::

    $ python atlascli.py -h
    usage: atlascli [-h] [--publickey PUBLICKEY] [--privatekey PRIVATEKEY]
                    [--atlasgroup ATLASGROUP] [--debug]

    A command line interface too the MongoDB Atlasdatabase as a
    service.https://www.mongodb.com/cloud/atlas for more infoSee also
    https://docs.atlas.mongodb.com/configure-api-access/#programmatic-api-keysFor
    how to obtain a programmatic API key required to access the API

    optional arguments:
      -h, --help            show this help message and exit
      --publickey PUBLICKEY
                            MongoDB Atlas public API key
      --privatekey PRIVATEKEY
                            MongoDB Atlas private API key
      --atlasgroup ATLASGROUP
                            Default group (aka project)
      --debug               Turn on logging at debug level

