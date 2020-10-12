## Manual Test for issue 29

from atlasapi.atlas import Atlas
from atlasapi.clusters import  AdvancedOptions, InstanceSizeName


a = Atlas(user="fuamsneq",password="dff5b500-95d2-4d5d-9dcd-da2150b0e68f",group="5b1e92c13b34b93b0230e6e1")


out =a.Clusters.modify_cluster_instance_size(cluster='oplogTest',new_cluster_size=InstanceSizeName.M20)

print(out)