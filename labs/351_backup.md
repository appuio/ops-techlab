Lab 5: Backup / Restore
============

In this techlab, we will create a Backup and learn, where the important files to backup are located. The full state of a cluster installation includes:

- etcd data on each master
- API objects (stored in etcd, but it's a good idea to regularly export all objects)
- Docker registry storage
- PV storage
- Certificates
- Ansible hosts file

Lab 5.1: Master Backup files
-------------
All files that are recommended to make a backup on the master are located in the following folders:

Ansible inventory file, that contains the information, how the cluster is build. 
```
/etc/ansible/hosts
```

Here are the master Configuration files, certificates and htpasswd located
```
/etc/origin/master/
```
These files should be backed up on all masters.

Lab 5.2: Node Backup files
-------------
All files that are recommended to make a backup on the nodes are located in the following folders:

Node Configuration files
```
/etc/origin/node/
```

On each node are the certs from the docker-registry.
```
/etc/docker/certs.d/
```

These files should be backed up on all nodes.


Lab 5.3: Application Backup
-------------

To make a backup of the data in the persistent volumes, you need to backup the volumes of your storage environment. If you are using glusterfs, it's recommended to mount all volumes and use an existing backup software to make a backup of all files in those mounts.

Lab 5.4: Project Backup
-------------
It is advisable to Backup regularly all project data.
Login to the first master and run the script. It will create a folders for each project with all Openshift API Objects in json.
```
[ec2-user@master1 ~]$ /home/ec2-user/resource/openshift-project-backup.sh
[ec2-user@master1 ~]$ ls -al /home/ec2-user/openshift_backup_*/projects
```

We will now delete the logging project and try to restore it from our backup.
```
[ec2-user@master1 ~]$ oc delete project logging
```

Check if the project is being deleted
```
[ec2-user@master1 ~]$ oc get project logging
```

Now we will restore the logging project from our backup
```
[ec2-user@master1 ~]$ oc new-project logging

[ec2-user@master1 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/serviceaccount.json
[ec2-user@master1 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/secret.json
[ec2-user@master1 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/configmap.json 
[ec2-user@master1 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/rolebindings.json
[ec2-user@master1 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/project.json
[ec2-user@master1 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/daemonset.json
```
Check if all pods are becoming ready
```
[ec2-user@master1 ~]$ oc get pods -w
```

If everything is ready, you can check, if you can login to Kibana and see that it's receiving logs again.
```
https://kibana.wildcard.[user].lab.openshift.ch
```

Lab 5.5: etcd Backup and complete Restore
-------------
## Create etcd Backup
To make a consistent etcd backup, we need to login to the master and make a cold backup of the etcd server:
```
[root@master1 ~]# systemctl stop etcd.service
[root@master1 ~]# etcdctl backup --data-dir /var/lib/etcd/ --backup-dir etcd.bak
[root@master1 ~]# cp /var/lib/etcd/member/snap/db etcd.bak/member/snap/
[root@master1 ~]# systemctl start etcd.service
```

Check if the etcd cluster is healthy.
```
[root@master1 ~]# etcdctl -C https://master1.[user].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://172.31.46.235:2379
cluster is healthy
```
## Restore etcd cluster
We will restore the etcd cluster now. 

First, we need to stop etcd on the first master.
```
[root@master1 ~]# systemctl stop etcd
```

The cluster is now down and you can't get any resources through the console. We are now copying the files back from the backup and set the right permissions.
```
[root@master1 ~]# ETCD_DIR=/var/lib/etcd/
[root@master1 ~]# mv $ETCD_DIR /var/lib/etcd.orig
[root@master1 ~]# cp -Rp etcd.bak $ETCD_DIR
[root@master1 ~]# chcon -R --reference /var/lib/etcd.orig/ $ETCD_DIR
[root@master1 ~]# chown -R etcd:etcd $ETCD_DIR
```

Add the "--force-new-cluster" parameter to the etcd unit file, start etcd and check if it's running. This is needed, because initially it will create a new cluster with the existing data from the backup. 
```
[root@master1 ~]# sed -i '/ExecStart/s/"$/  --force-new-cluster"/' /usr/lib/systemd/system/etcd.service
[root@master1 ~]# systemctl daemon-reload
[root@master1 ~]# systemctl start etcd
[root@master1 ~]# systemctl status etcd
```

The cluster is now initialized, so we need to remove the "--force-new-cluster" parameter again and restart etcd.
```
[root@master1 ~]# sed -i '/ExecStart/s/ --force-new-cluster//' /usr/lib/systemd/system/etcd.service
[root@master1 ~]# systemctl daemon-reload
[root@master1 ~]# systemctl restart etcd
[root@master1 ~]# systemctl status etcd
```

Check if etcd is healthy again and check if "/openshift.io" exists in etcd
```
[root@master1 ~]# etcdctl -C https://master1.[user].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://127.0.0.1:2379
cluster is healthy
[root@master1 ~]# etcdctl -C https://master1.[user].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key ls /
/openshift.io
```

we need to change the peerURL of the etcd to it's private ip.
```
[root@master1 ~]# etcdctl -C https://master1.[user].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key member list
92c764a37c90869: name=master1.[user].lab.openshift.ch peerURLs=https://localhost:2380 clientURLs=https://[private_ip]:2379 isLeader=true

[root@master1 ~]# etcdctl -C https://master1.[user].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key member update 6248d01c5701 https://[private_ip]:2379
Updated member with ID 6248d01c5701 in cluster

[root@master1 ~]# etcdctl -C https://master1.[user].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key member list
6248d01c5701: name=master1.[user].lab.openshift.ch peerURLs=https://172.31.46.201:2379 clientURLs=https://172.31.46.201:2379 isLeader=true
```

