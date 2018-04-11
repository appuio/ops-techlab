Lab 3.7: Upgrade Openshift from 3.6 to 3.7
============

In this techlab, we will upgrade our Openshifft 3.6 installation to Openshift 3.7

Lab 3.7.1: Upgrade to latest Openshift 3.6
-------------
Before upgrading to the next minor release, you need to upgrade to the latest asynchronous release of version 3.6.
https://docs.openshift.com/container-platform/3.6/release_notes/ocp_3_6_release_notes.html#ocp-36-asynchronous-errata-updates

The procedure is the same as upgrading to the next minor version. See next lab (Lab 3.5.2: Upgrade to latest Openshift 3.7)
As our lab is already on the latest asynchronous release of version 3.6, we can proceed to upgrade to latest Openshift 3.7.

Lab 3.7.2: Upgrade to latest Openshift 3.7
-------------
## Upgrade preparation
First we need to prepare our nodes and make sure, all instances have the new repository attached and the old removed.
```
[ec2-user@master0 ~]$ ansible all -m shell -a "subscription-manager refresh"
[ec2-user@master0 ~]$ ansible all -m shell -a 'subscription-manager repos --disable="rhel-7-server-ose-3.6-rpms" --enable="rhel-7-server-ose-3.7-rpms" --enable="rhel-7-server-extras-rpms" --enable="rhel-7-fast-datapath-rpms"'
[ec2-user@master0 ~]$ ansible all -m shell -a "yum clean all"
```

Next we need to upgrade atomic-openshift-utils to version 3.7 on our first master.
```
[ec2-user@master0 ~]$ sudo yum update -y atomic-openshift-utils
....
Updating:
 atomic-openshift-utils                              noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  354 k
Updating for dependencies:
 openshift-ansible                                   noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  328 k
 openshift-ansible-callback-plugins                  noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  319 k
 openshift-ansible-docs                              noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  341 k
 openshift-ansible-filter-plugins                    noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  331 k
 openshift-ansible-lookup-plugins                    noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  309 k
 openshift-ansible-playbooks                         noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  418 k
 openshift-ansible-roles                             noarch                  3.7.23-1.git.0.bc406aa.el7                     rhel-7-server-ose-3.7-rpms                  2.0 M
....
```

Change the following Ansible variables in our Openshift inventory:
```
[ec2-user@master0 ~]$ sudo vim /etc/ansible/hosts
....
openshift_pkg_version=-3.7.42
....
openshift_release=v3.7
```

## Upgrade procedure
1. Upgrade the master and API Objects.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/upgrades/v3_7/upgrade_control_plane.yml
...
```
2. Upgrade node by node manually because we need to make sure, that the nodes running GlusterFS in container have enough time to replicate to the other nodes.
Upgrade "node0.[user].lab.openshift.ch":
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/upgrades/v3_7/upgrade_nodes.yml --extra-vars "kubernetes.io/hostname=node0.[user].lab.openshift.ch"
...
```

Wait until all GlusterFS Pods are ready again and check if GlusterFS volumes have heal entries.
```
[ec2-user@master0 ~]$ oc project default
[ec2-user@master0 ~]$ oc get pods -o wide | grep glusterfs
usterfs-storage-b9xdl                       1/1       Running   0          23m       172.31.33.43    node0.user6.lab.openshift.ch
glusterfs-storage-lll7g                       1/1       Running   0          23m       172.31.43.209   node1.user6.lab.openshift.ch
glusterfs-storage-mw5sz                       1/1       Running   0          23m       172.31.34.222   node2.user6.lab.openshift.ch
[ec2-user@master0 ~]$ oc rsh <GlusterFS_pod_name>
[ec2-user@master0 ~]$ for vol in `gluster volume list`; do gluster volume heal $vol info; done | grep -i "number of entries"
Number of entries: 0
```

If all volumes have "Number of entries: 0", we can proceed with the next node and repeat the check of GlusterFS.

```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/upgrades/v3_7/upgrade_nodes.yml -e "kubernetes.io/hostname=node2.[user].lab.openshift.ch"
...
```
3. Upgrading the EFK Logging Stack
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-logging.yml
```

4. Upgrading Cluster Metrics
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-metrics.yml
```

5. To finish the upgrade it's best practice to run the config playbook
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/config.yml
```

6. If you are using the oc client outside of the Openshift Platform, you need to download the latest binary for the client and replace it. The binary is available for Linux, macOS and Windows. You can get it here:
```
https://console.user[X].lab.openshift.ch/console/extensions/clients/
```
Important: You need to tell all users of the platform to update their client.

Lab 3.7.3: Verify upgrade
-------------
Check rpm package version of docker and openshift on all nodes and master.
```
[ec2-user@master0 ~]$ ansible all -m shell -a "rpm -qi atomic-openshift | grep -i name -A1"
[ec2-user@master0 ~]$ ansible masters -m shell -a "rpm -qi atomic-openshift-master | grep -i name -A1"
[ec2-user@master0 ~]$ ansible all -m shell -a "rpm -qi atomic-openshift-node | grep -i name -A1"
[ec2-user@master0 ~]$ ansible all -m shell -a "rpm -qi docker | grep -i name -A3"
```

Check image version of registry, router, metrics and logging
```
[ec2-user@master0 ~]$ oc get pod -o yaml --all-namespaces | grep -i "image:.*.openshift3"
```

Now we need to verify our installation according to: "322_install_openshift => Verify Openshift installation"
- 3.2.2 [Install OpenShift](322_install_openshift.md)

---

**End of Lab 3.7**

[← back to overview](../README.md)
