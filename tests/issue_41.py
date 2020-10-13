from os import getenv, environ
from atlasapi.atlas import Atlas
from atlasapi.clusters import TLSProtocols
from datetime import datetime

USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)

a = Atlas(USER, API_KEY, GROUP_ID)

a.Clusters.modify_cluster_tls(cluster='CBTest',TLS_protocol=TLSProtocols.TLS1_0)
