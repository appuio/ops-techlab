## Lab 5.2: Restore

<a name="5.2.1">
### Lab 5.2.1: Restore a Project
</a>

We will now delete the logging project and try to restore it from the backup.
```
[ec2-user@master0 ~]$ oc delete project logging
```

Check if the project is being deleted
```
[ec2-user@master0 ~]$ oc get project logging
```

Restore the logging project from the backup. Some objects still exist, because they are not namespaced and therefore not deleted. You will see during the restore, that these object will not be replaced.
```
[ec2-user@master0 ~]$ oc adm new-project logging --node-selector=""
[ec2-user@master0 ~]$ oc project logging

[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/serviceaccount.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/secret.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/configmap.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/rolebindings.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/project.json
[ec2-user@master0 ~]$ oc create -f /home/ec2-user/openshift_backup_[date]/projects/logging/daemonset.json
```

Scale the logging components.
```
[ec2-user@master0 ~]$ oc get dc
NAME                  REVISION   DESIRED   CURRENT   TRIGGERED BY
logging-curator       5          1         1         config
logging-es-a4nhrowo   5          1         1         config
logging-kibana        7          1         0         config


[ec2-user@master0 ~]$ oc scale dc logging-kibana --replicas=0
[ec2-user@master0 ~]$ oc scale dc logging-curator --replicas=0
[ec2-user@master0 ~]$ oc scale dc logging-es-[HASH] --replicas=0
[ec2-user@master0 ~]$ oc scale dc logging-kibana --replicas=1
[ec2-user@master0 ~]$ oc scale dc logging-curator --replicas=1
[ec2-user@master0 ~]$ oc scale dc logging-es-[HASH] --replicas=1
``` 

Check if the pods are coming up again
```
[ec2-user@master0 ~]$ oc get pods -w
```

If all the pods are ready, Kibana should be receiving logs again.
```
https://logging.app[X].lab.openshift.ch
```


<a name="5.2.2">
### Lab 5.2.2: Restore the etcd Cluster ###
<a/>

:warning: Before you proceed, make sure you've already added master2 [LINK](https://github.com/gerald-eggenberger/ops-techlab/blob/release-3.11-backup/labs/35_add_new_node_and_master.md)

copy the snapshot to the master1.user[x].lab.openshift.ch
```
[ec2-user@master0 ~]$ userid=[x]
[ec2-user@master0 ~]$ scp /tmp/snapshot.db master1.user$userid.lab.openshift.ch:/tmp/snapshot.db
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=atomic-openshift-node state=stopped"
[ec2-user@master0 ~]$ ansible etcd -m service -a "name=docker state=stopped"
[ec2-user@master0 ~]$ ansible etcd -a "rm -rf /var/lib/etcd"
[ec2-user@master0 ~]$ ansible etcd -a "rmdir /var/lib/etcd"
[ec2-user@master0 ~]$ ansible etcd -a "mv /etc/etcd/etcd.conf /etc/etcd/etcd.conf.bak"
```

switch to user root and restore the etc-database

:warning: run this task on ALL Masters (master0,master1)
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

#### Check ectd-clusther health ####
```
[root@master0 ~]# ETCD_ALL_ENDPOINTS=` etcdctl3 --write-out=fields   member list | awk '/ClientURL/{printf "%s%s",sep,$3; sep=","}'`
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint status  --write-out=table
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint health
```

### Scale up the etcd Cluster ###
Add the third etcd master2.user[X].lab.openshift.ch to the etcd cluster
```
[ec2-user@master0 ~]$ sudo etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/origin/master/master.etcd-ca.crt --cert-file=/etc/origin/master/master.etcd-client.crt --key-file=/etc/origin/master/master.etcd-client.key member add master2.user[X].lab.openshift.ch https://[IP_OF_MASTER2]:2380
Added member named master2.user[X].lab.openshift.ch with ID aadb46077a7f58a to cluster

ETCD_NAME="master2.user[X].lab.openshift.ch"
ETCD_INITIAL_CLUSTER="master0.user[X].lab.openshift.ch=https://172.31.37.65:2380,master2.user[X].lab.openshift.ch=https://172.31.32.131:2380"
ETCD_INITIAL_CLUSTER_STATE="existing"
```

Login to `master2.user[X].lab.openshift.ch` and edit the etcd configuration file using the environment variables provided above. 
Then remove the etcd data directory and restart etcd.

```
[ec2-user@master2 ~]$ sudo vi /etc/etcd/etcd.conf
[ec2-user@master2 ~]$ sudo rm -rf /var/lib/etcd/member
[ec2-user@master2 ~]$ sudo systemctl restart etcd
```

#### Check ectd-clusther health ####
```
[root@master0 ~]# ETCD_ALL_ENDPOINTS=` etcdctl3 --write-out=fields   member list | awk '/ClientURL/{printf "%s%s",sep,$3; sep=","}'`
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint status  --write-out=table
[root@master0 ~]# etcdctl3 --endpoints=$ETCD_ALL_ENDPOINTS  endpoint health
```

Try to restore the last etcd on master2.user[X] the same way you did for master1.user[X].

---

**End of Lab 5.2**

<p width="100px" align="right"><a href="60_monitoring_troubleshooting.md">6. Monitoring and Troubleshooting →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
