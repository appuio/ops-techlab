# Appendix 3: Using AWS EBS and EFS Storage
This appendix is going to show you how to use AWS EBS and EFS Storage on OpenShift 3.11.

## Installation
:information_source: To access the efs-storage at aws, you will need an fsid. Please ask your instructor to get one.

Uncomment the following part in your Ansible inventory and set the fsid:
```
[ec2-user@master0 ~]$ sudo vi /etc/ansible/hosts
```

# EFS Configuration
```
openshift_provisioners_install_provisioners=True
openshift_provisioners_efs=True
openshift_provisioners_efs_fsid="[provided by instructor]"
openshift_provisioners_efs_region="eu-central-1"
openshift_provisioners_efs_nodeselector={"beta.kubernetes.io/os": "linux"}
openshift_provisioners_efs_aws_access_key_id="[provided by instructor]"
openshift_provisioners_efs_aws_secret_access_key="[provided by instructor]"
openshift_provisioners_efs_supplementalgroup=65534
openshift_provisioners_efs_path=/persistentvolumes
```

For detailed information about provisioners take a look at https://docs.openshift.com/container-platform/3.11/install_config/provisioners.html#provisioners-efs-ansible-variables

Execute the playbook to install the provisioner:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-provisioners/config.yml
```

Check if the pv was created:
```
[ec2-user@master0 ~]$ oc get pv

NAME               CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS    CLAIM                              STORAGECLASS   REASON    AGE
provisioners-efs   1Mi        RWX            Retain           Bound     openshift-infra/provisioners-efs                            22h
```


:warning: The external provisioner for AWS EFS on OpenShift Container Platform 3.11 is still a Technology Preview feature.
https://docs.openshift.com/container-platform/3.11/install_config/provisioners.html#overview

#### Create StorageClass

To enable dynamic provisioning, you need to crate a storageclass:
```
[ec2-user@master0 ~]$ cat << EOF > aws-efs-storageclass.yaml
kind: StorageClass
apiVersion: storage.k8s.io/v1beta1
metadata:
  name: nfs
provisioner: openshift.org/aws-efs 
EOF
[ec2-user@master0 ~]$ oc create -f aws-efs-storageclass.yaml
```

Check if the storage class has been created:
```
[ec2-user@master0 ~]$ oc get sc

NAME                PROVISIONER               AGE
glusterfs-storage   kubernetes.io/glusterfs   23h
nfs                 openshift.org/aws-efs     23h
```

#### Create PVC

Now we create a little project and claim a volume from EFS.

```
[ec2-user@master0 ~]$ oc new-project quotatest
[ec2-user@master0 ~]$ oc new-app centos/ruby-25-centos7~https://github.com/sclorg/ruby-ex.git
[ec2-user@master0 ~]$ cat << EOF > test-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: quotatest
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 10Mi
  storageClassName: nfs
EOF
[ec2-user@master0 ~]$ oc create -f test-pvc.yaml
[ec2-user@master0 ~]$ oc set volume dc/ruby-ex --add --overwrite --name=v1 --type=persistentVolumeClaim --claim-name=quotatest --mount-path=/quotatest
```

Check if we can see our pvc:
```
[ec2-user@master0 ~]$ oc get pvc

NAME               STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
quotatest          Bound     pvc-2fa78a43-98ee-11e9-94ce-064eab17d15e   10Mi       RWX            nfs            17m
```

We will now try to write 40Mi in the 10Mi claim to demonstrate, that PVs do not enforce quotas
```
[ec2-user@master0 ~]$ oc get pods
NAME                             READY     STATUS    RESTARTS   AGE
ruby-ex-2-zwnws                  1/1       Running   0          1h
[ec2-user@master0 ~]$ oc rsh ruby-ex-2-zwnws
$ df -h /quotatest
Filesystem                                                                                                               Size  Used Avail Use% Mounted on
fs-4f7f2916.efs.eu-central-1.amazonaws.com:/persistentvolumes/provisioners-efs-pvc-2fa78a43-98ee-11e9-94ce-064eab17d15e  8.0E     0  8.0E   0% /quotatest
$ dd if=/dev/urandom of=/quotatest/quota bs=4096 count=10000
```

#### Delete EFS Volumes
When you delete the PVC, the PV and the corresponding data gets deleted.

```
[ec2-user@master0 ~]$ oc get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS    CLAIM                              STORAGECLASS   REASON    AGE
provisioners-efs                           1Mi        RWX            Retain           Bound     openshift-infra/provisioners-efs                            23m
pvc-2fa78a43-98ee-11e9-94ce-064eab17d15e   10Mi       RWX            Delete           Bound     test/provisioners-efs              nfs                      17m
registry-volume                            5Gi        RWX            Retain           Bound     default/registry-claim                                      13m
[ec2-user@master0 ~]$ oc scale dc/ruby-ex --replicas=0
[ec2-user@master0 ~]$ oc delete pvc provisioners-efs
[ec2-user@master0 ~]$ oc get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS    CLAIM                              STORAGECLASS   REASON    AGE
provisioners-efs                           1Mi        RWX            Retain           Bound     openshift-infra/provisioners-efs                            23m
registry-volume                            5Gi        RWX            Retain           Bound     default/registry-claim                                      13m
```

Check if the efs-provisioner cleans up the NFS Volume:
```
[ec2-user@master0 ~]$ oc project openshift-infra
[ec2-user@master0 ~]$ oc get pods
NAME                             READY     STATUS    RESTARTS   AGE
provisioners-efs-1-l75qr         1/1       Running   0          1h
[ec2-user@master0 ~]$ oc rsh provisioners-efs-1-l75qr
sh-4.2# df /persistentvolumes
Filesystem                                                           1K-blocks    Used        Available Use% Mounted on
fs-4f7f2916.efs.eu-central-1.amazonaws.com:/persistentvolumes 9007199254739968       0 9007199254739968   0% /persistentvolumes
sh-4.2# ls /persistentvolumes
sh-4.2# 
```

---

[← back to the labs overview](../README.md)

