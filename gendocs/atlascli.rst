atlascli - A Command line program for MongoDB Atlas
====================================================

The command line help for atlascli.py::

    $ python atlascli/cli.py -h
    usage: atlascli [-h] [--publickey PUBLICKEY] [--privatekey PRIVATEKEY]
                [--atlasgroup ATLASGROUP] [--format {short,full}]
                [--resource {organization,project,cluster}] [--id ID]
                [--debug] [--list]

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
    --format {short,full}
                        Format for output of list command [default: short]
    --resource {organization,project,cluster}
                        Which resource type are we operating on:organization,
                        project or cluster? [default: cluster]
    --id ID               Specify a resource id
    --debug               Turn on logging at debug level [default: False]
    --list                List a set of resources [default: False]
