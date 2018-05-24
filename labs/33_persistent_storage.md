## Lab 3.3: Persistent Storage

In this lab we take a look at the OpenShift implementation of Container Native Storage using the `heketi-cli` to resize a volume.


### heketi-cli

The package `heketi-client` has been pre-installed for you on the bastion host. The package includes the `heketi-cli` command.
In order to use `heketi-cli`, we need the server's URL and admin key:
```
[ec2-user@master0 ~]$ oc describe pod -n glusterfs | grep HEKETI_ADMIN_KEY
      HEKETI_ADMIN_KEY:			[HEKETI_ADMIN_KEY]
```

We can then set variables with this information:
```
[ec2-user@master0 ~]$ export HEKETI_CLI_USER=admin
[ec2-user@master0 ~]$ export HEKETI_CLI_KEY="[HEKETI_ADMIN_KEY]"
[ec2-user@master0 ~]$ export HEKETI_CLI_SERVER=$(oc get svc/heketi-storage -n glusterfs --template "http://{{.spec.clusterIP}}:{{(index .spec.ports 0).port}}")
```

Verify that everything is set as it should:
```
[ec2-user@master0 ~]$ env | grep -i heketi
HEKETI_CLI_KEY=[PASSWORD]
HEKETI_CLI_SERVER=http://172.30.250.14:8080
HEKETI_CLI_USER=admin
```

Now we can run some useful commands for troubleshooting.

Get all volumes and then show details of a specific volume using its id:
```
[ec2-user@master0 ~]$ heketi-cli volume list
Id:255b9535ee460dfa696a7616b57a7035    Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf    Name:glusterfs-registry-volume
Id:e5baabb2bca5ba5cdd749d48d47c4e89    Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf    Name:heketidbstorage

[ec2-user@master0 ~]$ heketi-cli volume info 255b9535ee460dfa696a7616b57a7035
...
```

Get the cluster id and details of the cluster:
```
[ec2-user@master0 ~]$ heketi-cli cluster list
Clusters:
Id:bc64bf1b4a4e7cc0702d28c7c02674cf [file][block]
[ec2-user@master0 ~]$ heketi-cli cluster info bc64bf1b4a4e7cc0702d28c7c02674cf
...
```

Get nodes and details of a specific node using its id:
```
[ec2-user@master0 ~]$ heketi-cli node list
Id:3efc4d8267eb3b65c2d3ed9848aa4328	Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf
Id:c0de1021e7577c26721b22003c14427c	Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf
Id:c9612d0eee19146642f51dc2f3d484e5	Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf
[ec2-user@master0 ~]$ heketi-cli node info c9612d0eee19146642f51dc2f3d484e5
...
```

Show the whole topology:
```
[ec2-user@master0 ~]$ heketi-cli topology info
...
```


### Set Default Storage Class

A StorageClass provides a way to describe a certain type of storage. Different classes might map to different storage types (e.g. nfs, gluster, ...), quality-of-service levels, to backup policies or to arbitrary policies determined by the cluster administrators. In our case we only have one storage class which is `glusterfs-storage`:
```
[ec2-user@master0 ~]$ oc get storageclass
```

By setting the anotation `storageclass.kubernetes.io/is-default-class` on a StorageClass we make it the default storage class on an OpenShift cluster:
```
[ec2-user@master0 ~]$ oc patch storageclass glusterfs-storage -p  '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

If then someone creates a pvc and does not specify the StorageClass, the [DefaultStorageClass admission controller](https://kubernetes.io/docs/admin/admission-controllers/#defaultstorageclass) does automatically set the StorageClass to the DefaultStorageClass.

**Note:** We could have set the Ansible inventory variable `openshift_storage_glusterfs_storageclass_default` to `true` during installation in order to let the playbooks automatically do what we just did by hand. For demonstration purposes however we set it to `false`.


### Create and Delete a Persistent Volume Claim

If you create a PersistentVolumeClaim, Heketi will automatically create a PersistentVolume and bind it to your claim. Likewise if you delete a claim, Heketi will delete the PersistentVolume.

Create a new project and create a pvc:
```
[ec2-user@master0 ~]$ oc new-project labelle
Now using project "labelle" on server "https://console.user[X].lab.openshift.ch:8443".
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

Check if the pvc could be bound to a new volume:
```
[ec2-user@master0 ~]$ oc get pvc
NAME        STATUS    VOLUME                                     CAPACITY   ACCESSMODES   STORAGECLASS        AGE
testclaim   Bound     pvc-839223fd-30d4-11e8-89f3-067e4f48dfe4   1Gi        RWO           glusterfs-storage   38s

[ec2-user@master0 ~]$ oc get pv
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM                    STORAGECLASS        REASON    AGE
pvc-839223fd-30d4-11e8-89f3-067e4f48dfe4   1Gi        RWO           Delete          Bound     labelle/testclaim        glusterfs-storage             41s
...
```

Delete the claim and check if the volume gets deleted:
```
[ec2-user@master0 ~]$ oc delete pvc testclaim
persistentvolumeclaim "testclaim" deleted
[ec2-user@master0 ~]$ oc get pv

[ec2-user@master0 ~]$ oc delete project labelle
```


### Resize Existing Volume

We will resize the registry volume with heketi-cli.

First we need to know which volume is in use for the registry:
```
[ec2-user@master0 ~]$ oc get pvc registry-claim -n default
NAME             STATUS    VOLUME            CAPACITY   ACCESSMODES   STORAGECLASS   AGE
registry-claim   Bound     registry-volume   5Gi        RWX                          2d

[ec2-user@master0 ~]$ oc describe pv registry-volume | grep Path
    Path:		glusterfs-registry-volume

[ec2-user@master0 ~]$ heketi-cli volume list | grep glusterfs-registry-volume
Id:255b9535ee460dfa696a7616b57a7035    Cluster:bc64bf1b4a4e7cc0702d28c7c02674cf    Name:glusterfs-registry-volume
```

Now we can extend the volume from 5Gi to 6Gi:
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

In order for the persistent volume's information and the actually available space to be consistent, we're going to edit the pv's specification:
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

<p width="100px" align="right"><a href="34_renew_certificates.md">3.4 Renew Certificates →</a></p>

[← back to the Chapter Overview](30_daily_business.md)
