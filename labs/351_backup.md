Lab 3.5: Backup / Restore
============

In this techlab you will learn how to create a new backup and which files are important. The following items should be backuped:

- etcd data on each master
- API objects (stored in etcd, but it's a good idea to regularly export all objects)
- Docker registry storage
- PV storage
- Certificates
- Ansible hosts file

Lab 3.5.1: Master Backup files
-------------
The following files should be backuped on all masters:

- Ansible inventory file (contains information about the cluster): `/etc/ansible/hosts`
- Configuration files (for the master), certificates and htpasswd: `/etc/origin/master/`

Lab 3.5.2: Node Backup files
-------------
Backup the following folders on all nodes:

- Node Configuration files: `/etc/origin/node/`
- Certificates for the docker-registry: `/etc/docker/certs.d/`

Lab 3.5.3: Application Backup
-------------

To backup the data in persistent volumes, you should mount them somewhere. If you mount a Glusterfs volume, it is guaranteed to be consistent. The bricks directly on the Glusterfs servers can contain small inconsistencies that Glusterfs hasn't synced to the other instances yet.

Lab 3.5.4: Project Backup
-------------
It is advisable to regularly backup all project data.
The following script on the first master will export all the Openshift API Objects (in json) of all projects and save them to the filesystem.
```
[ec2-user@master0 ~]$ /home/ec2-user/resource/openshift-project-backup.sh
[ec2-user@master0 ~]$ ls -al /home/ec2-user/openshift_backup_*/projects
```

We will now delete the logging project and try to restore it from the backup.
```
[ec2-user@master0 ~]$ oc delete project logging
```

Check if the project is being deleted
```
[ec2-user@master0 ~]$ oc get project logging
```

Restore the logging project from the backup
```
[ec2-user@master0 ~]$ oc new-project logging

[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/serviceaccount.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/secret.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/configmap.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/rolebindings.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/project.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/daemonset.json
```
Check if the pods are coming up again
```
[ec2-user@master0 ~]$ oc get pods -w
```

If all the pods are ready, Kibana should be receiving logs again.
```
https://logging.app[USERID].lab.openshift.ch
```

Lab 3.5.5: etcd Backup and complete Restore
-------------
## Create etcd Backup
To ensure a consistent etcd backup, we need to stop the daemon. Since there are 3 etcd servers, there is no downtime. All the new data that gets written during this period gets synced after the etcd daemon is started again.
```
[root@master0 ~]# systemctl stop etcd.service
[root@master0 ~]# etcdctl backup --data-dir /var/lib/etcd/ --backup-dir etcd.bak
[root@master0 ~]# cp /var/lib/etcd/member/snap/db etcd.bak/member/snap/
[root@master0 ~]# systemctl start etcd.service
```

Check if the etcd cluster is healthy.
```
[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://172.31.46.235:2379
cluster is healthy
```
## Restore etcd cluster

First, we need to stop etcd on the first master.
```
[root@master0 ~]# systemctl stop etcd
```

The cluster is now down and you can't get any resources through the console. We are now copying the files back from the backup and set the right permissions.
```
[root@master0 ~]# ETCD_DIR=/var/lib/etcd/
[root@master0 ~]# mv $ETCD_DIR /var/lib/etcd.orig
[root@master0 ~]# cp -Rp etcd.bak $ETCD_DIR
[root@master0 ~]# chcon -R --reference /var/lib/etcd.orig/ $ETCD_DIR
[root@master0 ~]# chown -R etcd:etcd $ETCD_DIR
```

Add the "--force-new-cluster" parameter to the etcd unit file, start etcd and check if it's running. This is needed, because initially it will create a new cluster with the existing data from the backup.
```
[root@master0 ~]# sed -i '/ExecStart/s/"$/  --force-new-cluster"/' /usr/lib/systemd/system/etcd.service
[root@master0 ~]# systemctl daemon-reload
[root@master0 ~]# systemctl start etcd
[root@master0 ~]# systemctl status etcd
```

The cluster is now initialized, so we need to remove the "--force-new-cluster" parameter again and restart etcd.
```
[root@master0 ~]# sed -i '/ExecStart/s/ --force-new-cluster//' /usr/lib/systemd/system/etcd.service
[root@master0 ~]# systemctl daemon-reload
[root@master0 ~]# systemctl restart etcd
[root@master0 ~]# systemctl status etcd
```

Check if etcd is healthy and check if "/openshift.io" exists in etcd
```
[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://127.0.0.1:2379
cluster is healthy
[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key ls /
/openshift.io
```

We need to change the peerURL of the etcd to it's private ip. Make sure to
correctly copy the member_id and private_ip.
```
[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key member list
[member_id]: name=master0.user[X].lab.openshift.ch peerURLs=https://localhost:2380 clientURLs=https://[private_ip]:2379 isLeader=true

[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key member update [member_id] https://[private_ip]:2379
Updated member with ID 6248d01c5701 in cluster

[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key member list
6248d01c5701: name=master0.user[X].lab.openshift.ch peerURLs=https://172.31.46.201:2379 clientURLs=https://172.31.46.201:2379 isLeader=true
```

---

**End of Lab 3.5**

<p width="100px" align="right"><a href="360_monitoring_troubleshooting.md">Monitoring and Troubleshooting →</a></p>

[← back to overview](../README.md)
