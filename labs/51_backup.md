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
Let's gather the backup-script:
```
[ec2-user@master0 ~]$ sudo yum install git python-openshift -y
[ec2-user@master0 ~]$ git clone https://github.com/mabegglen/openshift-project-backup"
```
Now we create the cronjob on the first master:
```
[ec2-user@master0 ~]$ cd openshift-project-backup 
[ec2-user@master0 ~]$ ansible-playbook playbook.yml \
-e openshift_project_backup_job_name="cronjob-project-backup" \
-e "openshift_project_backup_schedule=\"0 6,18 * * *\"" \
-e openshift_project_backup_job_service_account="project-backup" \
-e openshift_project_backup_namespace="project-backup" \
-e openshift_project_backup_image="registry.access.redhat.com/openshift3/jenkins-slave-base-rhel7" \
-e openshift_project_backup_image_tag="v3.11" \
-e openshift_project_backup_storage_size="1G" \
-e openshift_project_backup_deadline="3600" \
-e openshift_project_backup_cronjob_api="batch/v1beta1"
```
Details https://github.com/mabegglen/openshift-project-backup

If you want to reschedule your backup-job to check it's functionality to every 1minute:

Change the value of schedule: to "*/1 * * * *"
```
[ec2-user@master0 ~]$ oc project project-backup
[ec2-user@master0 ~]$ oc get cronjob
[ec2-user@master0 ~]$ oc edit cronjob cronjob-project-backup
```

Show if cronjob is active:
```
[ec2-user@master0 openshift-project-backup]$ oc get cronjob
NAME                     SCHEDULE      SUSPEND   ACTIVE    LAST SCHEDULE   AGE
cronjob-project-backup   */1 * * * *   False     1         1m              48m
```

Show if backup-pod was launched:
```
[ec2-user@master0 openshift-project-backup]$ oc get pods
NAME                                      READY     STATUS      RESTARTS   AGE
cronjob-project-backup-1561384620-kjm6v   1/1       Running     0          47s
```

Check the logfiles while backup-job is running:
```
[ec2-user@master0 openshift-project-backup]$ oc logs <cronjob-project-backup-NAME> -f
```
When your Backupjob runs as expected, don't forget to set up the cronjob back to "0 22 * * *" for example.
```
[ec2-user@master0 ~]$ oc edit cronjob cronjob-project-backup
```

### Create etcd Backup
We plan to create a Backup of our etcd. When we've created our backup, we wan't to restore them on master1/master2 and scale out from 1 to 3 nodes.

First we create a snapshot of our etc-database:
```
[root@master0 ~]# export ETCD_POD_MANIFEST="/etc/origin/node/pods/etcd.yaml"
[root@master0 ~]# export ETCD_EP=$(grep https ${ETCD_POD_MANIFEST} | cut -d '/' -f3)
[root@master0 ~]# export ETCD_POD=$(oc get pods -n kube-system | grep -o -m 1 '\S*etcd\S*')
[root@master0 ~]# oc project kube-system
Now using project "kube-system" on server "https://internalconsole.user[x].lab.openshift.ch:443".
[root@master0 ~]# oc exec ${ETCD_POD} -c etcd -- /bin/bash -c "ETCDCTL_API=3 etcdctl \
 --cert /etc/etcd/peer.crt \
 --key /etc/etcd/peer.key \
 --cacert /etc/etcd/ca.crt \
 --endpoints $ETCD_EP \
 snapshot save /var/lib/etcd/snapshot.db" 

 Snapshot saved at /var/lib/etcd/snapshot.db
```
Check Filesize of the snapshot created:
```
[root@master0 ~]# ls -hl /var/lib/etcd/snapshot.db
-rw-r--r--. 1 root root 21M Jun 24 16:44 /var/lib/etcd/snapshot.db
```

copy them to the tmp directory for further use:
```
[root@master0 ~]# cp /var/lib/etcd/snapshot.db /tmp/snapshot.db
[root@master0 ~]# cp /var/lib/etcd/member/snap/db /tmp/db
```

:warning: Before you proceed, make sure you've already added master2 [LINK](https://github.com/gerald-eggenberger/ops-techlab/blob/release-3.11-backup/labs/35_add_new_node_and_master.md)

copy the snapshot to the master1/master2.user[x].lab.openshift.ch
```
[ec2-user@master0 ~]$ userid=[x]
[ec2-user@master0 ~]$ scp /tmp/snapshot.db master1.user$userid.lab.openshift.ch:/tmp/snapshot.db
[ec2-user@master0 ~]$ scp /tmp/snapshot.db master2.user$userid.lab.openshift.ch:/tmp/snapshot.db
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=atomic-openshift-node state=stopped"
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=docker state=stopped"
[ec2-user@master0 ~]$ ansible etcd -a "rm -rf /var/lib/etcd"
[ec2-user@master0 ~]$ ansible etcd -a "mv /etc/etcd/etcd.conf /etc/etcd/etcd.conf.bak"
```

switch to user root and restore the etc-database
run this task on ALL Masters (master0,master1,master2)
```
[ec2-user@master0 ~]$ sudo -i
[root@master0 ~]# yum install etcd-3.2.22-1.el7.x86_64
[root@master0 ~]# mv /etc/etcd/etcd.conf.bak /etc/etcd/etcd.conf
[root@master0 ~]# source /etc/etcd/etcd.conf
[root@master0 ~]# export ETCDCTL_API=3
[root@master0 ~]# ETCDCTL_API=3 etcdctl snapshot restore /tmp/snapshot.db \
  --name $ETCD_NAME \
  --initial-cluster $ETCD_INITIAL_CLUSTER \
  --initial-cluster-token $ETCD_INITIAL_CLUSTER_TOKEN \
  --initial-advertise-peer-urls $ETCD_INITIAL_ADVERTISE_PEER_URLS \
  --data-dir /var/lib/etcd
[root@master0 ~]# restorecon -Rv /var/lib/etcd
```

Start Services on etcd-nodes
```
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=docker state=started"
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=atomic-openshift-node state=started"
[ec2-user@master0 ~]$ sudo -i 
[root@master0 ~]# ETCD_ALL_ENDPOINTS=` etcdctl3 --write-out=fields   member list | awk '/ClientURL/{printf "%s%s",sep,$3; sep=","}'`
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint status  --write-out=table
```

---

**End of Lab 5.1**

<p width="100px" align="right"><a href="52_restore.md">5.2 Restore →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
