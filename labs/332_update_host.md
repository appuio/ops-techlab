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
node1.[user].lab.openshift.ch | SUCCESS | rc=0 >>
exclude= tuned-profiles-atomic-openshift-node  atomic-openshift-tests  atomic-openshift-sdn-ovs  atomic-openshift-recycle  atomic-openshift-pod  atomic-openshift-node  atomic-openshift-master  atomic-openshift-dockerregistry  atomic-openshift-clients-redistributable  atomic-openshift-clients  atomic-openshift  docker*1.20*  docker*1.19*  docker*1.18*  docker*1.17*  docker*1.16*  docker*1.15*  docker*1.14*  docker*1.13*
...
```

These excludes are set by using the official Openshift playbooks or when using the binary atomic-openshift-excluder and atomic-openshift-docker-excluder directly.
We remove now the excludes and set it again for demonstration purpose. This is sometimes required, if you need to patch a system without using the Openshift playbooks and there are dependency errors.
```
[ec2-user@master0 ~]$ ansible all -m shell -a "atomic-openshift-excluder unexclude && atomic-openshift-docker-excluder unexclude"
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
[ec2-user@master0 ~]$ ansible all -m shell -a "atomic-openshift-excluder exclude && atomic-openshift-docker-excluder exclude"
[ec2-user@master0 ~]$ ansible all -m shell -a "grep exclude /etc/yum.conf"
```

## Apply OS patches to masters and nodes
First login as cluster-admin and drain the first node.
```
[ec2-user@master0 ~]$ oc get nodes
[ec2-user@master0 ~]$ oc adm drain node1.[user].lab.openshift.ch --ignore-daemonsets --delete-local-data
```

If you list all running pods on the node you should see, that just the DaemonSets (glusterfs-storage and logging-fluentd) are left.
```
[ec2-user@master0 ~]$ oc adm manage-node node1.[user].lab.openshift.ch --list-pods
Listing matched pods on node: node1.user6.lab.openshift.ch

NAME                      READY     STATUS    RESTARTS   AGE
glusterfs-storage-1758r   1/1       Running   1          2d
logging-fluentd-s2k2j     1/1       Running   0          1h
```

Let's check if the node is unscheduled.
```
[ec2-user@master0 ~]$ oc get nodes
...
node1.[user].lab.openshift.ch     Ready,SchedulingDisabled   2d        v1.6.1+5115d708d7
...

```
If everthing is ok, you can apply all OS patches and make a reboot.
We exclude the Openshift repository, because these packages are managed by the Openshift playbooks.
```
[ec2-user@master0 ~]$ ansible node1.[user].lab.openshift.ch -m shell -a 'yum update -y --disablerepo=rhel-7-server-ose-3.6-rpms'
[ec2-user@master0 ~]$ ansible node1.[user].lab.openshift.ch -m shell -a 'systemctl reboot'
```

Wait until the node becomes available again and schedule it again. Be careful, as it takes some time, until the node becomes unready.
```
[ec2-user@master0 ~]$ oc get nodes -w
[ec2-user@master0 ~]$ oc adm manage-node node1.[user].lab.openshift.ch --schedulable
```

Check if all pods will be properly created again on this node.
```
[ec2-user@master0 ~]$ oc adm manage-node node1.[user].lab.openshift.ch --list-pods

Listing matched pods on node: node1.user6.lab.openshift.ch

NAME                      READY     STATUS    RESTARTS   AGE
glusterfs-storage-1758r   1/1       Running   2          2d
router-1-cc21f            1/1       Running   0          4m
logging-fluentd-s2k2j     1/1       Running   1          1h
```

You need to repeat this steps on all other Instances to make sure, the whole cluster has the current OS Patches. Master don't need to be drained, as they are not scheduled and there are no running pods on them.

---

**End of Lab 3.3.2**

<p width="100px" align="right"><a href="333_persistent_storage.md">Persistent storage →</a></p>

[← back to overview](../README.md)
