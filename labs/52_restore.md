## Lab 5.2: Restore

### Restore a Project

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


### Restore the etcd Cluster

First, we need to stop all etcd and delete the corresponding data:
```
[ec2-user@master0 ~]$ ansible etcd -m "file" -a "path=/etc/origin/node/pods-stopped state=directory"
[ec2-user@master0 ~]$ ansible etcd -m "shell" -a "mv /etc/origin/node/pods/etcd.yaml /etc/origin/node/pods-stopped/"
[ec2-user@master0 ~]$ ansible etcd -m "file" -a "path=/var/lib/etcd state=absent"
```

Prepare etcd directories:
```
[ec2-user@master0 ~]$ ansible etcd -m "file" -a "path=/var/lib/etcd state=directory group=etcd owner=etcd recurse=yes"
[ec2-user@master0 ~]$ ansible etcd -a "restorecon -Rv /var/lib/etcd/"
```

Get Information on existing cluster:
```
[root@master0 ~]# grep -i ETCD_INITIAL_ADVERTISE_PEER_URLS /etc/etcd/etcd.conf 
ETCD_INITIAL_ADVERTISE_PEER_URLS=https://172.31.42.72:2380
```

Restore etcd data from snapshot using the information above:
```
[root@master0 ~]# etcdctl3 snapshot restore /var/lib/etcd/snapshot.db \
                           --data-dir /var/lib/etcd/ \
	                   --name "master0.user[X].lab.openshift.ch" \
                      	   --initial-cluster "master0.user[X].lab.openshift.ch=https://[MASTER0_IP_FROM_ETCD_INITIAL_ADVERTISE_PEER_URLS]:2380" \
             	           --initial-cluster-token etcd-cluster-1 \
                           --initial-advertise-peer-urls https://[MASTER0_IP_FROM_ETCD_INITIAL_ADVERTISE_PEER_URLS]:2380 \
                           --skip-hash-check=true"
```

Start first etcd:
```
[ec2-user@master0 ~]$ ansible master0 -m "shell" -a "mv /etc/origin/node/pods-stopped/etcd.yaml /etc/origin/node/pods/"
```

We are now running on a single etcd setup. To get HA again, we need to scaleup to at least three etcds.

First add the new etcds host in the Ansible inventory in the (`[new_etcd]`) section and add it to the (`[OSEv3:children]` group).
```
[OSEv3:children]
...
new_etcd

[new_etcd]
master1.user7.lab.openshift.ch
master2.user7.lab.openshift.ch

```

### Scaleup to a HA etcd cluster

Execute the playbook responsible for the etcd scaleup:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/scaleup.yml
```


## Verification and Finalization

Verify your installation now consists of the original cluster plus one new etcd member:
```
[root@master0 ~]# etcdctl2 --cert-file=/etc/etcd/peer.crt \
                           --key-file=/etc/etcd/peer.key \
                           --ca-file=/etc/etcd/ca.crt \
                           --peers="https://master0.user[X].lab.openshift.ch:2379,https://master1.user[X].lab.openshift.ch:2379" \
                           cluster-health
```

Move the now functional etcd members from the group `[new_etcd]` to `[etcd]` in your Ansible inventory at `/etc/ansible/hosts` so the group looks like:
```
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
