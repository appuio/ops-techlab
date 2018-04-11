Lab 3.3: Daily business
============

Lab 3.3.5: Add a new OpenShift node and master
-------------
In this lab we take a look how to add a new node and a new master to our Openshift Cluster.

## Scaleup node
Uncomment the new_node (node3.user) in the Ansible inventory and uncomment new_nodes in the "[OSEv3:children]" section.
```
[root@master0 ec2-user]# vi /etc/ansible/hosts
...
#nfs
#new_masters
new_nodes
glusterfs
...
[new_nodes]
node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}" openshift_schedulable=false
...

```
Host preparation

We will run an Ansible playbook, that will install all the required prerequisites and recommendations.
- Enable the required Repos
-- rhel-7-server-rpms
-- rhel-7-server-extras-rpms
-- rhel-7-server-optional-rpms
-- rhel-7-fast-datapath-rpms
-- rhel-7-server-ose-3.6
- Install prerequisites packages https://docs.openshift.com/container-platform/3.6/install_config/install/host_preparation.html#installing-base-packages

Check if the hosts are available on ssh with Ansible and run the pre-install playbook.
```
[ec2-user@master0 ~]$ ansible node3.user[X].lab.openshift.ch -m ping
[ec2-user@master0 ~]$ ansible-playbook resource/pre-install.yml --limit=node3.user[X].lab.openshift.ch
```

Now we can run the scaleup playbook provided by Red Hat for the node scaleup.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-node/scaleup.yml
```

Check if the node is ready.
```
[ec2-user@master0 ~]$ oc get nodes
NAME                             STATUS                     AGE       VERSION
master0.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
master1.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
node0.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node1.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node2.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node3.user[X].lab.openshift.ch     Ready,SchedulingDisabled   1m        v1.6.1+5115d708d7
```

Schedule the new node, drain another worker node and see, if the pods are running correctly on the new node.
```
[ec2-user@master0 ~]$ oc adm manage-node node3.user[X].lab.openshift.ch --schedulable
[ec2-user@master0 ~]$ oc adm drain node2.user[X].lab.openshift.ch --ignore-daemonsets --delete-local-data
[ec2-user@master0 ~]$ watch "oc adm manage-node node3.user[X].lab.openshift.ch --list-pods"
```

If everything works as expected, we schedule the node again and move the new node from the "new_nodes" section in the Ansible inventory to the nodes section.
```
[ec2-user@master0 ~]$ oc adm manage-node node2.user[X].lab.openshift.ch --schedulable
[root@master0 ~]$ vi /etc/ansible/hosts
[nodes]
master0.user[X].lab.openshift.ch openshift_hostname=master0.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
master1.user[X].lab.openshift.ch openshift_hostname=master1.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
node0.user[X].lab.openshift.ch openshift_hostname=node0.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
node1.user[X].lab.openshift.ch openshift_hostname=node1.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
node2.user[X].lab.openshift.ch openshift_hostname=node2.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}"
node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}"

```
Uncomment the new node from the new_nodes section.
```
vi /etc/ansible/hosts
...
[new_nodes]
#node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}" openshift_schedulable=false
...

```

## Scaleup the new master

Uncomment the new master to the Ansible inventory. It needs to be in both sections (new_nodes and new_masters).
```
[root@master0 ~]# vi /etc/ansible/hosts
...
etcd
#lb
#nfs
new_masters
new_nodes
glusterfs
...
[new_nodes]
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false

[new_masters]
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
..
```

Check if the host is available on ssh with Ansible and run the pre-install playbook.
```
[ec2-user@master0 ~]$ ansible master2.user[X].lab.openshift.ch -m ping
[ec2-user@master0 ~]$ ansible-playbook resource/pre-install.yml
```

Now we can add the new master.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-master/scaleup.yml
```

Let's check if the node daemon on the new master is ready
```
[ec2-user@master0 ~]$ oc get nodes
NAME                             STATUS                     AGE       VERSION
master0.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
master1.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
master2.user[X].lab.openshift.ch   Ready,SchedulingDisabled   10m       v1.6.1+5115d708d7
node0.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node1.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node2.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node3.user[X].lab.openshift.ch     Ready                      32m       v1.6.1+5115d708d7
```

Check if the old masters see the new master:
```
[ec2-user@master0 ~]$ journalctl -u atomic-openshift-master-api | grep master2.user[X].lab.openshift.ch
Apr 04 07:31:00 master0.user[X].lab.openshift.ch atomic-openshift-master-api[3626]: I0404 07:31:00.942109    3626 rest.go:324] Starting watch for /api/v1/nodes, rv=8732 labels= fields=metadata.name=master2.user[X].lab.openshift.ch timeout=9m10s
...
```

If everything works as expected, we need to move the new master from the "new_masters" section in the Ansible inventory to the masters and nodes section
```
[root@master0 ~]# vi /etc/ansible/hosts
[masters]
master0.user[X].lab.openshift.ch
master1.user[X].lab.openshift.ch
master2.user[X].lab.openshift.ch
...

[nodes]
master0.user[X].lab.openshift.ch openshift_hostname=master0.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
master1.user[X].lab.openshift.ch openshift_hostname=master1.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
node0.user[X].lab.openshift.ch openshift_hostname=node0.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
node1.user[X].lab.openshift.ch openshift_hostname=node1.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
node2.user[X].lab.openshift.ch openshift_hostname=node2.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}"
node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}"
...
```

Uncomment the new master from the new_nodes and new_master section.
```
[root@master0 ~]# vi /etc/ansible/hosts
...
[new_nodes]
#node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}" openshift_schedulable=false
#master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false

[new_masters]
#master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
```

Now, you need to add the new master as a target to your Load Balancers, so it receives traffic.

---

**End of Lab 3.3.5**

<p width="100px" align="right"><a href="351_backup.md">Backup / Restore →</a></p>

[← back to overview](../README.md)
