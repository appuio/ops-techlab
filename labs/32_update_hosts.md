## Lab 3.2: Update Hosts

### OpenShift Excluder
In this lab we take a look at the OpenShift excluders, apply OS updates to all nodes, drain, reboot and schedule them again.

The config playbook we use to install and configure OpenShift removes yum excludes for specific packages at its beginning. Likewise it adds them back at the end of the playbook run. This makes it possible to update OpenShift-specific packages during a playbook run but freeze these package versions during e.g. a `yum update`.

First, let's check if the excludes have been set on all nodes. Connect to the first master and run:
```
[ec2-user@master0 ~]$ ansible nodes -m shell -a "atomic-openshift-excluder status && atomic-openshift-docker-excluder status"
...
app-node0.user[X].lab.openshift.ch | SUCCESS | rc=0 >>
exclude -- All packages excluded
exclude -- All packages excluded
...
```

These excludes are set by using the OpenShift Ansible playbooks or when using the command `atomic-openshift-excluder` or `atomic-openshift-docker-excluder`. For demonstration purposes, we will now remove and set these excludes again.

```
[ec2-user@master0 ~]$ ansible nodes -m shell -a "atomic-openshift-excluder unexclude && atomic-openshift-docker-excluder unexclude"
[ec2-user@master0 ~]$ ansible nodes -m shell -a "atomic-openshift-excluder status && atomic-openshift-docker-excluder status"
[ec2-user@master0 ~]$ ansible nodes -m shell -a "atomic-openshift-excluder exclude && atomic-openshift-docker-excluder exclude"
[ec2-user@master0 ~]$ ansible nodes -m shell -a "atomic-openshift-excluder status && atomic-openshift-docker-excluder status"
```


### Apply OS Patches to Masters and Nodes

If you don't know if you're cluster-admin or not.
Query all users with rolebindings=cluster-admin:
```
oc get clusterrolebinding -o json | jq '.items[] | select(.metadata.name |  startswith("cluster-admin")) | .userNames'
```

Hint: root on master-node always is system:admin (don't use it for ansible-tasks). But you're able to grant permissions to other users.

First, login as cluster-admin and drain the first app-node (this deletes all pods so the OpenShift scheduler creates them on other nodes and also disables scheduling of new pods on the node).
```
[ec2-user@master0 ~]$ oc get nodes
[ec2-user@master0 ~]$ oc adm drain app-node0.user[X].lab.openshift.ch --ignore-daemonsets --delete-local-data
```

After draining a node, only pods from DaemonSets should remain on the node:
```
[ec2-user@master0 ~]$ oc adm manage-node app-node0.user[X].lab.openshift.ch --list-pods

Listing matched pods on node: app-node0.user[X].lab.openshift.ch

NAMESPACE              NAME                    READY     STATUS    RESTARTS   AGE
openshift-logging      logging-fluentd-lfjnc   1/1       Running   0          33m
openshift-monitoring   node-exporter-czhr2     2/2       Running   0          36m
openshift-node         sync-rhh8z              1/1       Running   0          46m
openshift-sdn          ovs-hz9wj               1/1       Running   0          46m
openshift-sdn          sdn-49tpr               1/1       Running   0          46m
```

Scheduling should now be disabled for this node:
```
[ec2-user@master0 ~]$ oc get nodes
...
app-node0.user[X].lab.openshift.ch     Ready,SchedulingDisabled   compute   2d        v1.11.0+d4cacc0
...

```

If everything looks good, you can update the node and reboot it. The first command can take a while and doesn't output anything until it's done:
```
[ec2-user@master0 ~]$ ansible app-node0.user[X].lab.openshift.ch -m yum -a "name='*' state=latest exclude='atomic-openshift-* openshift-* docker-*'"
[ec2-user@master0 ~]$ ansible app-node0.user[X].lab.openshift.ch --poll=0 --background=1 -m shell -a 'sleep 2 && reboot'
```

After the node becomes ready again, enable schedulable anew. Do not do this before the node has rebooted (it takes a while for the node's status to change to `Not Ready`):
```
[ec2-user@master0 ~]$ oc get nodes -w
[ec2-user@master0 ~]$ oc adm manage-node app-node0.user[X].lab.openshift.ch --schedulable
```

Check that pods are correctly starting:
```
[ec2-user@master0 ~]$ oc adm manage-node app-node0.user[X].lab.openshift.ch --list-pods

Listing matched pods on node: app-node0.user[X].lab.openshift.ch

NAMESPACE              NAME                    READY     STATUS    RESTARTS   AGE
dakota                 ruby-ex-1-6lc87         1/1       Running   0          12m
openshift-logging      logging-fluentd-lfjnc   1/1       Running   1          43m
openshift-monitoring   node-exporter-czhr2     2/2       Running   2          47m
openshift-node         sync-rhh8z              1/1       Running   1          56m
openshift-sdn          ovs-hz9wj               1/1       Running   1          56m
openshift-sdn          sdn-49tpr               1/1       Running   1          56m
```

Since we want to update the whole cluster, **you will need to repeat these steps on all servers**. Masters do not need to be drained because they do not run any pods (unschedulable by default).

---

**End of Lab 3.2**

<p width="100px" align="right"><a href="33_persistent_storage.md">3.3 Persistent Storage →</a></p>

[← back to the Chapter Overview](30_daily_business.md)
