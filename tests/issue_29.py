## Manual Test for issue 29

from atlasapi.atlas import Atlas
from atlasapi.clusters import  AdvancedOptions, InstanceSizeName


a = Atlas(user="",password="",group="")


out =a.Clusters.modify_cluster_instance_size(cluster='oplogTest',new_cluster_size=InstanceSizeName.M10)

print(out)