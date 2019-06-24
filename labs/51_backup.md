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
- Docker configurations: /etc/sysconfig/docker /etc/sysconfig/docker-network /etc/sysconfig/docker-storage


### Node Backup Files

Backup the following folders on all nodes:

- Node Configuration files: `/etc/origin/node/`
- Certificates for the docker-registry: `/etc/docker/certs.d/`
- Docker configurations: /etc/sysconfig/docker /etc/sysconfig/docker-network /etc/sysconfig/docker-storage


### Application Backup

To backup the data in persistent volumes, you should mount them somewhere. If you mount a Glusterfs volume, it is guaranteed to be consistent. The bricks directly on the Glusterfs servers can contain small inconsistencies that Glusterfs hasn't synced to the other instances yet.


### Project Backup

It is advisable to regularly backup all project data.
We will set up a cronjob in a project called "project-backup" which hourly writes all resources on OpenShift to a PV.
Let's login to our Jumphost first and gather/deloy the backup-script:
```
[ec2-user@jump.lab.openshift.ch] cd /home/ec2-user/resource
[ec2-user@jump.lab.openshift.ch] userid=[ID]
[ec2-user@jump.lab.openshift.ch] ansible -i setup-inventory master0 -m shell -e "userid=$userid" -a " \
sudo yum install git python-openshift -y && git clone https://github.com/mabegglen/openshift-project-backup"
```
Now we create the cronjob
```
[ec2-user@master0 ~]$ cd openshift-project-backup && ansible-playbook playbook.yml \
-e openshift_project_backup_job_name="cronjob-project-backup" \
-e openshift_project_backup_schedule="0 * * * * "
-e openshift_project_backup_job_service_account="project-backup"
-e openshift_project_backup_namespace="project-backup"
-e openshift_project_backup_image="registry.access.redhat.com/openshift3/jenkins-slave-base-rhel7"
-e openshift_project_backup_image_tag="v3.11"
-e openshift_project_backup_storage_size="1G"
-e openshift_project_backup_deadline="3600"
-e openshift_project_backup_cronjob_api="batch/v1beta1"
```
Details https://github.com/mabegglen/openshift-project-backup


### Create etcd Backup

To ensure a consistent etcd backup, we need to stop the daemon. Since there are 3 etcd servers, there is no downtime. All the new data that gets written during this period gets synced after the etcd daemon is started again.



[ec2-user@master0 ~]$ sudo etcdctl backup --data-dir /var/lib/etcd/ --backup-dir etcd.bak
[ec2-user@master0 ~]$ sudo cp /var/lib/etcd/member/snap/db etcd.bak/member/snap/
[ec2-user@master0 ~]$ sudo systemctl start etcd.service
```

Check if the etcd cluster is healthy.
```
[ec2-user@master0 ~]$ sudo etcdctl -C https://master0.user[X].lab.openshift.ch:2379,https://master1.user[X].lab.openshift.ch:2379,https://master2.user[X].lab.openshift.ch:2379 --ca-file=/etc/etcd/ca.crt --cert-file=/etc/etcd/peer.crt --key-file=/etc/etcd/peer.key cluster-health
member 3f511408a118b9fd is healthy: got healthy result from https://172.31.37.59:2379
member 50953a25943f54a8 is healthy: got healthy result from https://172.31.35.180:2379
member ec41afe89f86deaf is healthy: got healthy result from https://172.31.35.199:2379
cluster is healthy
```


---

**End of Lab 5.1**

<p width="100px" align="right"><a href="52_restore.md">5.2 Restore →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
