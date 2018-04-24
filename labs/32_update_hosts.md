## Lab 3.2: Update hosts

### OpenShift excluder
In this lab we take a look at the OpenShift excluders, apply OS updates to all nodes, drain, reboot and schedule them again.

The config playbook we use to install and configure OpenShift removes yum excludes for specific packages at its beginning. Likewise it adds them back at the end of the playbook run. This makes it possible to update OpenShift-specific packages during a playbook run but freeze these package versions during e.g. a `yum update`.

First, let's check if the excludes have been set on all nodes. Connect to the first master and run:
```
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
...
node1.user[X].lab.openshift.ch | SUCCESS | rc=0 >>
exclude= tuned-profiles-atomic-openshift-node  atomic-openshift-tests  atomic-openshift-sdn-ovs  atomic-openshift-recycle  atomic-openshift-pod  atomic-openshift-node  atomic-openshift-master  atomic-openshift-dockerregistry  atomic-openshift-clients-redistributable  atomic-openshift-clients  atomic-openshift  docker*1.20*  docker*1.19*  docker*1.18*  docker*1.17*  docker*1.16*  docker*1.15*  docker*1.14*  docker*1.13*
...
```

These excludes are set by using the OpenShift Ansible playbooks or when using the command `atomic-openshift-excluder` or `atomic-openshift-docker-excluder`. For demonstration purposes, we will now remove and set these excludes again.

```
[ec2-user@master0 ~]$ ansible all -m shell -a "atomic-openshift-excluder unexclude && atomic-openshift-docker-excluder unexclude"
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
[ec2-user@master0 ~]$ ansible all -m shell -a "atomic-openshift-excluder exclude && atomic-openshift-docker-excluder exclude"
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
```


### Apply OS patches to masters and nodes

First, login as cluster-admin and drain the first node (this deletes all pods so the OpenShift scheduler creates them on other nodes and also disables scheduling of new pods on the node).
```
[ec2-user@master0 ~]$ oc get nodes
[ec2-user@master0 ~]$ oc adm drain node1.user[X].lab.openshift.ch --ignore-daemonsets --delete-local-data
```

After draining a node, only the DaemonSets (`glusterfs-storage` and `logging-fluentd`) should remain on the node:
```
[ec2-user@master0 ~]$ oc adm manage-node node1.user[X].lab.openshift.ch --list-pods
Listing matched pods on node: node1.user[X].lab.openshift.ch

NAME                      READY     STATUS    RESTARTS   AGE
glusterfs-storage-1758r   1/1       Running   1          2d
logging-fluentd-s2k2j     1/1       Running   0          1h
```

Scheduling should now be disabled for this node:
```
[ec2-user@master0 ~]$ oc get nodes
...
node1.user[X].lab.openshift.ch     Ready,SchedulingDisabled   2d        v1.6.1+5115d708d7
...

```

If everything looks good, you can update the node and reboot it. The first command can take a while and doesn't output anything until it's done:
```
[ec2-user@master0 ~]$ ansible node1.user[X].lab.openshift.ch -m yum -a "name='*' state=latest"
[ec2-user@master0 ~]$ ansible node1.user[X].lab.openshift.ch --poll=0 --background=1 -a 'sleep 2 && reboot'
```

After the node becomes ready again, enable schedulable anew. Do not do this before the node has rebooted (it takes a while for the node's status to change to `Not Ready`):
```
[ec2-user@master0 ~]$ oc get nodes -w
[ec2-user@master0 ~]$ oc adm manage-node node1.user[X].lab.openshift.ch --schedulable
```

Check that pods are correctly starting:
```
[ec2-user@master0 ~]$ oc adm manage-node node1.user[X].lab.openshift.ch --list-pods

Listing matched pods on node: node1.user[X].lab.openshift.ch

NAME                      READY     STATUS    RESTARTS   AGE
glusterfs-storage-1758r   1/1       Running   2          2d
router-1-cc21f            1/1       Running   0          4m
logging-fluentd-s2k2j     1/1       Running   1          1h
```

Since we want to update the whole cluster, you will need to repeat these steps on all servers. Masters do not need to be drained because they do not run any pods (unschedulable by default).

---

**End of lab 3.2**

<p width="100px" align="right"><a href="33_persistent_storage.md">3.3 Persistent storage →</a></p>

[← back to the chapter overview](30_daily_business.md)
