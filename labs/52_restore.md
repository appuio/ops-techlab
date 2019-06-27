## Lab 5.2: Restore

<a name="5.2.1"> </a>
### Lab 5.2.1: Restore a Project

We will now delete the initially created `dakota` project and try to restore it from the backup.
```
[ec2-user@master0 ~]$ oc delete project dakota
```

Check if the project is being deleted
```
[ec2-user@master0 ~]$ oc get project dakota
```

Restore the dakota project from the backup.
```
[ec2-user@master0 ~]$ oc new-project dakota
[ec2-user@master0 ~]$ oc project project-backup
[ec2-user@master0 ~]$ oc debug `oc get pods -o jsonpath='{.items[*].metadata.name}' | awk '{print $1}'`
sh-4.2# tar -xvf /backup/backup-201906131343.tar.gz -C /tmp/
sh-4.2# oc apply -f /tmp/dakota/
```

Start build and push image to registry
```
[ec2-user@master0 ~]$ oc start-build ruby-ex -n dakota
``` 

Check whether the pods become ready again.
```
[ec2-user@master0 ~]$ oc get pods -w -n dakota
```

<a name="5.2.2"></a>
### Lab 5.2.2: Restore the etcd Cluster ###

:warning: Before you proceed, make sure you've already added master2 [Lab 3.5.2](35_add_new_node_and_master.md#3.5.2)

copy the snapshot to the master1.user[x].lab.openshift.ch
```
[ec2-user@master0 ~]$ userid=[x]
[ec2-user@master0 ~]$ scp /tmp/snapshot.db master1.user$userid.lab.openshift.ch:/tmp/snapshot.db
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=atomic-openshift-node state=stopped"
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=docker state=stopped"
[ec2-user@master0 ~]$ ansible etcd -a "rm -rf /var/lib/etcd"
[ec2-user@master0 ~]$ ansible etcd -a "mv /etc/etcd/etcd.conf /etc/etcd/etcd.conf.bak"
```

switch to user root and restore the etc-database

:warning: run this task on ALL Masters (master0,master1)
```
[ec2-user@master0 ~]$ sudo -i
[root@master0 ~]# yum install etcd-3.2.22-1.el7.x86_64
[root@master0 ~]# rmdir /var/lib/etcd
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

As we have restored the etcd on all masters we should be able to start the services:
```
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=docker state=started"
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=atomic-openshift-node state=started"
```

#### Check ectd-clusther health ####
```
[root@master0 ~]# ETCD_ALL_ENDPOINTS=` etcdctl3 --write-out=fields   member list | awk '/ClientURL/{printf "%s%s",sep,$3; sep=","}'`
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint status  --write-out=table
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint health
```

### Scale up the etcd Cluster ###
Add the third etcd master2.user[X].lab.openshift.ch to the etcd cluster
We add the 3rd Node (master2) by adding it to the [new_etcd] group and activate this group by uncommenting it:
```
[OSEv3:children]
...
new_etcd 

[new_etcd] 
master2.user[X].lab.openshift.ch 
```

:warning: the scaleup-playbook provided by redhat doesn't restart the masters seamlessly. If you have to scaleup in production, please do this in a maintenance window.

Run the scaleup-Playbook to scaleup the etcd-cluster:

```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/scaleup.yml
```

#### Check ectd-clusther health ####
```
[root@master0 ~]# ETCD_ALL_ENDPOINTS=` etcdctl3 --write-out=fields   member list | awk '/ClientURL/{printf "%s%s",sep,$3; sep=","}'`
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint status  --write-out=table
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint health
```

:information_source: don't get confused by the 4 entries. Master0 will show up twice with the same id

You should now get an output like this.

```
+---------------------------------------------+------------------+---------+---------+-----------+-----------+------------+
|                  ENDPOINT                   |        ID        | VERSION | DB SIZE | IS LEADER | RAFT TERM | RAFT INDEX |
+---------------------------------------------+------------------+---------+---------+-----------+-----------+------------+
| https://master0.user1.lab.openshift.ch:2379 | a8e78dd0690640cb |  3.2.22 |   26 MB |     false |         2 |       9667 |
|                   https://172.31.42.95:2379 | 1ab823337d6e84bf |  3.2.22 |   26 MB |     false |         2 |       9667 |
|                   https://172.31.38.22:2379 | 56f5e08139a21df3 |  3.2.22 |   26 MB |      true |         2 |       9667 |
|                  https://172.31.46.194:2379 | a8e78dd0690640cb |  3.2.22 |   26 MB |     false |         2 |       9667 |
+---------------------------------------------+------------------+---------+---------+-----------+-----------+------------+

https://172.31.46.194:2379 is healthy: successfully committed proposal: took = 2.556091ms
https://172.31.42.95:2379 is healthy: successfully committed proposal: took = 2.018976ms
https://master0.user1.lab.openshift.ch:2379 is healthy: successfully committed proposal: took = 2.639024ms
https://172.31.38.22:2379 is healthy: successfully committed proposal: took = 1.666699ms
```

#### move new etcd-member in /etc/ansible/hosts ####

Move the now functional etcd members from the group `[new_etcd]` to `[etcd]` in your Ansible inventory at `/etc/ansible/hosts` so the group looks like:


```
...
#new_etcd

#[new_etcd]

...

[etcd]
master0.user[X].lab.openshift.ch
master1.user[X].lab.openshift.ch
master2.user[X].lab.openshift.ch
```

---

**End of Lab 5.2**

<p width="100px" align="right"><a href="60_monitoring_troubleshooting.md">6. Monitoring and Troubleshooting →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
