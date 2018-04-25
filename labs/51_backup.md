## Lab 5.1: Backup

In this techlab you will learn how to create a new backup and which files are important. The following items should be backuped:

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


### Node Backup Files

Backup the following folders on all nodes:

- Node Configuration files: `/etc/origin/node/`
- Certificates for the docker-registry: `/etc/docker/certs.d/`


### Application Backup

To backup the data in persistent volumes, you should mount them somewhere. If you mount a Glusterfs volume, it is guaranteed to be consistent. The bricks directly on the Glusterfs servers can contain small inconsistencies that Glusterfs hasn't synced to the other instances yet.


### Project Backup

It is advisable to regularly backup all project data.
The following script on the first master will export all the OpenShift API Objects (in json) of all projects and save them to the filesystem.
```
[ec2-user@master0 ~]$ /home/ec2-user/resource/openshift-project-backup.sh
[ec2-user@master0 ~]$ ls -al /home/ec2-user/openshift_backup_*/projects
```


### Create etcd Backup

To ensure a consistent etcd backup, we need to stop the daemon. Since there are 3 etcd servers, there is no downtime. All the new data that gets written during this period gets synced after the etcd daemon is started again.
```
[ec2-user@master0 ~]$ sudo systemctl stop etcd.service
[ec2-user@master0 ~]$ sudo etcdctl backup --data-dir /var/lib/etcd/ --backup-dir etcd.bak
[ec2-user@master0 ~]$ sudo cp /var/lib/etcd/member/snap/db etcd.bak/member/snap/
[ec2-user@master0 ~]$ sudo systemctl start etcd.service
```

Check if the etcd cluster is healthy.
```
[ec2-user@master0 ~]$ sudo etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://172.31.46.235:2379
cluster is healthy
```


---

**End of Lab 5.1**

<p width="100px" align="right"><a href="52_restore.md">5.2 Restore →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
