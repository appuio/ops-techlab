Lab 3: Daily business
============

Lab 3.3: Persistent storage
-------------
In this lab we take a look at the OpenShift implementation of Container Native Storage using the heketi-cli to resize a volume.

## heketi-cli
First we need to install the Heketi client rpm. We will use the client from the community upstream project for this lab. In production enviroment, you should use the client, provided by RedHat.
```
[ec2-user@master0 ~]$ sudo yum install -y https://buildlogs.centos.org/centos/7/storage/x86_64/gluster-4.0/heketi-client-6.0.0-1.el7.x86_64.rpm
```

Now we need the URL and admin Key to access the Heketi API.
```
[ec2-user@master0 ~]$ oc describe pod -n default| grep HEKETI_ADMIN_KEY
      HEKETI_ADMIN_KEY:			[HEKETI_ADMIN_KEY]
```

We can set the information in variables
```
[ec2-user@master0 ~]$ export HEKETI_CLI_USER=admin
[ec2-user@master0 ~]$ export HEKETI_CLI_KEY="[HEKETI_ADMIN_KEY]"
[ec2-user@master0 ~]$ export HEKETI_CLI_SERVER=$(oc get svc/heketi-storage -n default --template "http://{{.spec.clusterIP}}:{{(index .spec.ports 0).port}}")
```

Verify if everything is set as it should
```
[ec2-user@master0 ~]$ env | grep -i heketi
HEKETI_CLI_KEY=[PASSWORD]
HEKETI_CLI_SERVER=http://172.30.250.14:8080
HEKETI_CLI_USER=admin
```

Now we can run some useful commands for troubleshooting.

Get all volumes and show details of a volume
```
[ec2-user@master0 ~]$ heketi-cli volume list
Id:255b9535ee460dfa696a7616b57a7035    Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf    Name:glusterfs-registry-volume
Id:e5baabb2bca5ba5cdd749d48d47c4e89    Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf    Name:heketidbstorage
[ec2-user@master0 ~]$ heketi-cli volume info 255b9535ee460dfa696a7616b57a7035
...
```

Get Cluster id and get details of the cluster.
```
[ec2-user@master0 ~]$ heketi-cli cluster list
Clusters:
Id:bc64bf1b4a4e7cc0702d28c7c02674cf [file][block]
[ec2-user@master0 ~]$ heketi-cli cluster info bc64bf1b4a4e7cc0702d28c7c02674cf
...
```

Get nodes and get details of a node
```
[ec2-user@master0 ~]$ heketi-cli node list
Id:3efc4d8267eb3b65c2d3ed9848aa4328	Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf
Id:c0de1021e7577c26721b22003c14427c	Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf
Id:c9612d0eee19146642f51dc2f3d484e5	Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf
[ec2-user@master0 ~]$ heketi-cli node info c9612d0eee19146642f51dc2f3d484e5
...
```

Show the whole topology
```
[ec2-user@master0 ~]$ heketi-cli topology info
...
```

## Set default storage class
A StorageClass provides a way to describe a certain type of storage. Different classes might map to different storage types (e.g. nfs, gluster, ...), quality-of-service levels, to backup policies, or to arbitrary policies determined by the cluster administrators. In our case we only have one storage class which is `glusterfs-storage`:
```
[ec2-user@master0 ~]$ oc get storageclass
```

By setting the anotation `storageclass.kubernetes.io/is-default-class` on a StorageClass we set the DefaultStorageClass. In our case we set the default to `glusterfs-storage`:
```
[ec2-user@master0 ~]$ oc patch storageclass glusterfs-storage -p  '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```
If then someone creates a pvc and does not specify the StorageClass, the [DefaultStorageClass admission controller](https://kubernetes.io/docs/admin/admission-controllers/#defaultstorageclass) does automatically set the StorageClass to the DefaultStorageClass, which is `glusterfs-storage` in our case.

## Create and delete a pvc
If you create a pvc, Heketi will automatically create a pv and bind it to your pvc. Also if you delete a pvc, Heketi will delete the pv.

Create a new project and create a pvc
```
[ec2-user@master0 ~]$ oc new-project test
Now using project "test" on server "https://console.user[X].lab.openshift.ch:8443".
...
[ec2-user@master0 ~]$ cat <<EOF >pvc.yaml
apiVersion: "v1"
kind: "PersistentVolumeClaim"
metadata:
  name: "testclaim"
spec:
  accessModes:
    - "ReadWriteOnce"
  resources:
    requests:
      storage: "1Gi"
EOF

[ec2-user@master0 ~]$ oc create -f pvc.yaml
persistentvolumeclaim "testclaim" created
```

Check if pvc can be claimed and check the created pv.
```
[ec2-user@master0 ~]$ oc get pvc
NAME        STATUS    VOLUME                                     CAPACITY   ACCESSMODES   STORAGECLASS        AGE
testclaim   Bound     pvc-839223fd-30d4-11e8-89f3-067e4f48dfe4   1Gi        RWO           glusterfs-storage   38s

[ec2-user@master0 ~]$ oc get pv
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM                    STORAGECLASS        REASON    AGE
pvc-839223fd-30d4-11e8-89f3-067e4f48dfe4   1Gi        RWO           Delete          Bound     test/testclaim           glusterfs-storage             41s
...
```

Delete pvc and check if the pv gets deleted.
```
[ec2-user@master0 ~]$ oc delete pvc testclaim
persistentvolumeclaim "testclaim" deleted
[ec2-user@master0 ~]$ oc get pv

[ec2-user@master0 ~]$ oc delete project test
```

## Resize existing volume
We will resize the registry volume with heketi-cli.

First we need to know, which volume name is used for the registry.
```
[ec2-user@master0 ~]$ oc get pvc registry-claim -n default
NAME             STATUS    VOLUME            CAPACITY   ACCESSMODES   STORAGECLASS   AGE
registry-claim   Bound     registry-volume   5Gi        RWX                          2d

[ec2-user@master0 ~]$ oc describe pv registry-volume | grep Path
    Path:		glusterfs-registry-volume

[ec2-user@master0 ~]$ heketi-cli volume list | grep glusterfs-registry-volume
Id:255b9535ee460dfa696a7616b57a7035    Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf    Name:glusterfs-registry-volume

```

Now we can extend the volume from 5Gi to 6Gi
```
[ec2-user@master0 ~]$ heketi-cli volume expand --volume=255b9535ee460dfa696a7616b57a7035 --expand-size=1
Name: glusterfs-registry-volume
Size: 6
...
```
Check if the gluster volume has the new size:
```
[ec2-user@master0 ~]$ ansible all -m shell -a "df -ah" | grep glusterfs-registry-volume
172.31.40.96:glusterfs-registry-volume  6.0G  317M  5.7G   3% /var/lib/origin/openshift.local.volumes/pods/d8dc2712-3bcf-11e8-90a6-066961eacc9a/volumes/kubernetes.io~glusterfs/registry-volume
```


To use the space, we need to extend the pv also.
```
[ec2-user@master0 ~]$ oc get pv
NAME              CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM                    STORAGECLASS   REASON    AGE
registry-volume   5Gi        RWX           Retain          Bound     default/registry-claim                            1d
[ec2-user@master0 ~]$ oc patch pv registry-volume -p '{"spec":{"capacity":{"storage":"6Gi"}}}'
[ec2-user@master0 ~]$ oc get pv
NAME              CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM                    STORAGECLASS   REASON    AGE
registry-volume   6Gi        RWX           Retain          Bound     default/registry-claim                            1d
```

---

**End of Lab 3.3**

<p width="100px" align="right"><a href="34_renew_certificates.md">Renew certificates →</a></p>

[← back to overview](../README.md)
