## Lab 5.1: Backup

In this techlab you will learn how to create a new backup and which files are important. The following items should be backuped:

- Cluster data files
- etcd data on each master
- API objects (stored in etcd, but it's a good idea to regularly export all objects)
- Docker registry storage
- PV storage
- Certificates
- Ansible hosts file


### Master Backup Files

The following files should be backuped on all masters:

- Ansible inventory file (contains information about the cluster): `/etc/ansible/hosts`
- Configuration files (for the master), certificates and htpasswd: `/etc/origin/master/`
- Docker configurations: `/etc/sysconfig/docker` `/etc/sysconfig/docker-network` `/etc/sysconfig/docker-storage`

### Node Backup Files

Backup the following folders on all nodes:

- Node Configuration files: `/etc/origin/node/`
- Certificates for the docker-registry: `/etc/docker/certs.d/`
- Docker configurations: `/etc/sysconfig/docker` `/etc/sysconfig/docker-network` `/etc/sysconfig/docker-storage`

### Application Backup

To backup the data in persistent volumes, you should mount them somewhere. If you mount a Glusterfs volume, it is guaranteed to be consistent. The bricks directly on the Glusterfs servers can contain small inconsistencies that Glusterfs hasn't synced to the other instances yet.


### Project Backup

It is advisable to regularly backup all project data.
We have prior set up a cronjob in the project-backup project which hourly writes all resources on OpenShift to a PV.

### Create etcd Backup

Create the etcd data backup.
```
usernr=[ID]
[root@master0 ~]# etcdctl3 --cert /etc/etcd/peer.crt \
                           --key /etc/etcd/peer.key \
                           --cacert /etc/etcd/ca.crt \
                           --endpoints "https://master0.user$usernr.lab.openshift.ch:2379" \
                           endpoint health
https://master0.user1.lab.openshift.ch:2379 is healthy: successfully committed proposal: took = 1.308347ms
https://master0.user1.lab.openshift.ch:2379 is healthy: successfully committed proposal: took = 2.303151ms


[root@master0 ~]# etcdctl3 --cert /etc/etcd/peer.crt \
                           --key /etc/etcd/peer.key \
                           --cacert /etc/etcd/ca.crt \
                           --endpoints "https://master0.user$usernr.lab.openshift.ch:2379" \
                           snapshot save /var/lib/etcd/snapshot.db"
```

The snapshot has been created in the container. Therefore it could only be written to `/var/lib/etcd/`. For this reason the snapshot and the DB have to be copied away.
```
[root@master0 ~]# mkdir /var/lib/etcd/etcd.bak/
[root@master0 ~]# cp /var/lib/etcd/snapshot.db /var/lib/etcd/etcd.bak/
[root@master0 ~]# cp /var/lib/etcd/member/snap/db /var/lib/etcd/etcd.bak/
```

Check if the etcd cluster is healthy.
```
[root@master0 ~]# etcdctl3 --cert /etc/etcd/peer.crt \
                           --key /etc/etcd/peer.key \
                           --cacert /etc/etcd/ca.crt \
                           --endpoints "https://master0.user$usernr.lab.openshift.ch:2379" \
                           endpoint health
https://master0.user1.lab.openshift.ch:2379 is healthy: successfully committed proposal: took = 1.373096ms
https://master0.user1.lab.openshift.ch:2379 is healthy: successfully committed proposal: took = 1.656468ms

[root@master0 ~]# etcdctl3 --cert /etc/etcd/peer.crt \
                           --key /etc/etcd/peer.key \
                           --cacert /etc/etcd/ca.crt \
                           --endpoints "https://master0.user$usernr.lab.openshift.ch:2379" \
                           endpoint status
https://master0.user1.lab.openshift.ch:2379, cf42363b9a3c5327, 3.2.22, 22 MB, true, 120, 15669
https://master0.user1.lab.openshift.ch:2379, cf42363b9a3c5327, 3.2.22, 22 MB, true, 120, 15669
```


---

**End of Lab 5.1**

<p width="100px" align="right"><a href="52_restore.md">5.2 Restore →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
