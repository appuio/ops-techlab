Lab 3.3: Daily business
============

Lab 3.3.2: Update Host
-------------

## Openshift excluder
In this lab we take a look at the Openshift excluders, apply OS updates to all nodes, drain, reboot and schedule them again.

During the installation of Openshift or when running the config Playbook, openshift removes and adds excludes for certain rpm packages. This can cause trouble during upgrade of non OSE packages.

First, let's check if the excludes are set by Openshift on all nodes. Connect to the first master and run:
```
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
...
node1.user[X].lab.openshift.ch | SUCCESS | rc=0 >>
exclude= tuned-profiles-atomic-openshift-node  atomic-openshift-tests  atomic-openshift-sdn-ovs  atomic-openshift-recycle  atomic-openshift-pod  atomic-openshift-node  atomic-openshift-master  atomic-openshift-dockerregistry  atomic-openshift-clients-redistributable  atomic-openshift-clients  atomic-openshift  docker*1.20*  docker*1.19*  docker*1.18*  docker*1.17*  docker*1.16*  docker*1.15*  docker*1.14*  docker*1.13*
...
```

These excludes are set by using the official Openshift playbooks or when using the binary atomic-openshift-excluder and atomic-openshift-docker-excluder directly. For demonstration purposes, we will now remove and set the excludes again. This is required if you are manually patching a system or there are dependency errors. 

```
[ec2-user@master0 ~]$ ansible all -m shell -a "atomic-openshift-excluder unexclude && atomic-openshift-docker-excluder unexclude"
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
[ec2-user@master0 ~]$ ansible all -m shell -a "atomic-openshift-excluder exclude && atomic-openshift-docker-excluder exclude"
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
```

## Apply OS patches to masters and nodes
First login as cluster-admin and drain the first node (this deleten all pods, so they migrate to other nodes and also disables scheduling). 
```
[ec2-user@master0 ~]$ oc get nodes
[ec2-user@master0 ~]$ oc adm drain node1.user[X].lab.openshift.ch --ignore-daemonsets --delete-local-data
```

After draining a node, only the DaemonSets (glusterfs-storage and logging-fluentd) should be left running on the node.
```
[ec2-user@master0 ~]$ oc adm manage-node node1.user[X].lab.openshift.ch --list-pods
Listing matched pods on node: node1.user[X].lab.openshift.ch

NAME                      READY     STATUS    RESTARTS   AGE
glusterfs-storage-1758r   1/1       Running   1          2d
logging-fluentd-s2k2j     1/1       Running   0          1h
```

The node should now be unscheduled.
```
[ec2-user@master0 ~]$ oc get nodes
...
node1.user[X].lab.openshift.ch     Ready,SchedulingDisabled   2d        v1.6.1+5115d708d7
...

```
If everything looks ok, you can update the node and restart.
```
[ec2-user@master0 ~]$ ansible node1.user[X].lab.openshift.ch -m yum -a "name='*' state=latest"
[ec2-user@master0 ~]$ ansible node1.user[X].lab.openshift.ch -m shell -a 'systemctl reboot'
```

After the node becomes ready, set it schedulable again. Don't do this before the node has rebooted (the node can take a while to change to unready, during the reboot)
```
[ec2-user@master0 ~]$ oc get nodes -w
[ec2-user@master0 ~]$ oc adm manage-node node1.user[X].lab.openshift.ch --schedulable
```

Check that pods are correctly starting.
```
[ec2-user@master0 ~]$ oc adm manage-node node1.user[X].lab.openshift.ch --list-pods

Listing matched pods on node: node1.user6.lab.openshift.ch

NAME                      READY     STATUS    RESTARTS   AGE
glusterfs-storage-1758r   1/1       Running   2          2d
router-1-cc21f            1/1       Running   0          4m
logging-fluentd-s2k2j     1/1       Running   1          1h
```

Since we want to update the whole cluster, you will need to repeat these steps on all the instances. Masters don't need to be drained, because they do not run any pods (unschedulable by default).

---

**End of Lab 3.3.2**

<p width="100px" align="right"><a href="333_persistent_storage.md">Persistent storage →</a></p>

[← back to overview](../README.md)
