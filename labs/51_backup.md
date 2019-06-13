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
We have prior set up a cronjob in the project-backup project which writes all resources on OpenShift to a PV at 6:00 and 18:00.

### Create etcd Backup

Create the etcd data backup.
```
[root@master0 ~]# etcdctl3 --cert /etc/etcd/peer.crt \
                           --key /etc/etcd/peer.key \
                           --cacert /etc/etcd/ca.crt \
                           --endpoints "https://master1.user[X].lab.openshift.ch:2379" \
                           snapshot save /var/lib/etcd/snapshot.db"
```

Check if the etcd cluster is healthy.
```
[root@master0 ~]# etcdctl2 --cert-file=/etc/etcd/peer.crt \
                           --key-file=/etc/etcd/peer.key \
                           --ca-file=/etc/etcd/ca.crt \
                           --peers="https://master1.user[X].lab.openshift.ch:2379" \
                           cluster-health
member 50953a25943f54a8 is healthy: got healthy result from https://172.31.35.180:2379
member ec41afe89f86deaf is healthy: got healthy result from https://172.31.35.199:2379
cluster is healthy
```


---

**End of Lab 5.1**

<p width="100px" align="right"><a href="52_restore.md">5.2 Restore →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
