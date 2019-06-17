## Lab 7.1: Upgrade OpenShift 3.11.88 to 3.11.104

### Upgrade Preparation

We first need to make sure our lab environment fulfills the requirements mentioned in the official documentation. We are going to do an "[Automated In-place Cluster Upgrade](https://docs.openshift.com/container-platform/3.11/upgrading/automated_upgrades.html)" which lists part of these requirements and explains how to verify the current installation. Also check the [Prerequisites](https://docs.openshift.com/container-platform/3.11/install/prerequisites.html#install-config-install-prerequisites) of the new release.

Conveniently, our lab environment already fulfills all the requirements, so we can move on to the next step. 

#### 1. Ensure the openshift_deployment_type=openshift-enterprise ####
```
[ec2-user@master0 ~]$ grep -i openshift_deployment_type /etc/ansible/hosts
```

#### 2. disable rolling, full system restarts of the hosts ####
```
[ec2-user@master0 ~]$ ansible masters -m shell -a "grep -i openshift_rolling_restart_mode /etc/ansible/hosts"
```
in our lab environment this parameter isn't set, so let's do it on all master-nodes:
```
[ec2-user@master0 ~]$ ansible masters -m lineinfile -a 'path="/etc/ansible/hosts" regexp="^openshift_rolling_restart_mode" line="openshift_rolling_restart_mode=services" state="present"'
```
#### 3. change the value of openshift_pkg_version to 3.11.104 in /etc/ansible/hosts ####
```
[ec2-user@master0 ~]$ ansible masters -m lineinfile -a 'path="/etc/ansible/hosts" regexp="^openshift_pkg_version" line="openshift_pkg_version=-3.11.104" state="present"'
```
#### 4. upgrade the nodes ####

##### 4.1 prepare nodes for upgrade #####
```
[ec2-user@master0 ~]$ ansible all -a 'subscription-manager refresh'
[ec2-user@master0 ~]$ ansible all -a 'subscription-manager repos --enable="rhel-7-server-ose-3.11-rpms" --enable="rhel-7-server-rpms" --enable="rhel-7-server-extras-rpms" --enable="rhel-7-server-ansible-2.6-rpms" --enable="rhel-7-fast-datapath-rpms" --disable="rhel-7-server-ose-3.10-rpms" --disable="rhel-7-server-ansible-2.4-rpms"' 
[ec2-user@master0 ~]$ ansible all -a 'yum clean all'
[ec2-user@master0 ~]$ ansible masters -m lineinfile -a 'path="/etc/ansible/hosts" regexp="^openshift_certificate_expiry_fail_on_warn" line="openshift_certificate_expiry_fail_on_warn=False" state="present"'
```
##### 4.2 prepare your upgrade-host #####
```
[ec2-user@master0 ~]$ sudo -i
[ec2-user@master0 ~]# yum update -y openshift-ansible
```

##### 4.3 upgrade the control plane #####

Upgrade the so-called control plane, consisting of:

- etcd
- master components
- node services running on masters
- Docker running on masters
- Docker running on any stand-alone etcd hosts

```
[ec2-user@master0 ~]$ cd /usr/share/ansible/openshift-ansible
[ec2-user@master0 ~]$ ansible-playbook playbooks/byo/openshift-cluster/upgrades/v3_11/upgrade_control_plane.yml
```

##### 4.4 upgrade the nodes manually (one by one) #####

Upgrade node by node manually because we need to make sure, that the nodes running GlusterFS in container have enough time to replicate to the other nodes. 

Upgrade "infra-node0.user[X].lab.openshift.ch":
```
[ec2-user@master0 ~]$ ansible-playbook playbooks/byo/openshift-cluster/upgrades/v3_11/upgrade_nodes.yml --extra-vars openshift_upgrade_nodes_label="kubernetes.io/hostname=infra-node0.user[X].lab.openshift.ch"
```
Wait until all GlusterFS Pods are ready again and check if GlusterFS volumes have heal entries.
```
[ec2-user@master0 ~]$ oc project glusterfs
[ec2-user@master0 ~]$ oc get pods -o wide | grep glusterfs
[ec2-user@master0 ~]$ oc rsh <GlusterFS_pod_name>
sh-4.2# for vol in `gluster volume list`; do gluster volume heal $vol info; done | grep -i "number of entries"
Number of entries: 0
```
If all volumes have "Number of entries: 0", we can proceed with the next node and repeat the check of GlusterFS.

Upgrade "infra-node1.user[X].lab.openshift.ch":
```
[ec2-user@master0 ~]$ ansible-playbook playbooks/byo/openshift-cluster/upgrades/v3_11/upgrade_nodes.yml --extra-vars openshift_upgrade_nodes_label="kubernetes.io/hostname=infra-node1.user[X].lab.openshift.ch"
```

#### 5. Upgrading the EFK Logging Stack ####

**Note:** Setting openshift_logging_install_logging=true enables you to upgrade the logging stack.

```
[ec2-user@master0 ~]$ grep openshift_logging_install_logging /etc/ansible/hosts
[ec2-user@master0 ~]$ cd /usr/share/ansible/openshift-ansible/playbooks
[ec2-user@master0 ~]$ ansible-playbook openshift-logging/config.yml
[ec2-user@master0 ~]$ oc delete pod --selector="component=fluentd" -n logging
```

#### 6. Upgrading Cluster Metrics ####
```
[ec2-user@master0 ~]$ cd /usr/share/ansible/openshift-ansible/playbooks
[ec2-user@master0 ~]$ ansible-playbook openshift-metrics/config.yml
```

#### 7. Update the oc binary ####
The `atomic-openshift-clients-redistributable` package which provides the `oc` binary for different operating systems needs to be updated separately:
```
[ec2-user@master0 ~]$ ansible masters -a "yum install --assumeyes --disableexcludes=all atomic-openshift-clients-redistributable"
```

#### 8. Update oc binary on client ####
Update the `oc` binary on your own client. As before, you can get it from:
```
https://console.user[X].lab.openshift.ch/console/extensions/clients/
```

**Note:** You should tell all users of your platform to update their client. Client and server version differences can lead to compatibility issues.

---

**End of Lab 7.1**

<p width="100px" align="right"><a href="72_upgrade_verification.md">7.2 Verify the Upgrade →</a></p>

[← back to the Chapter Overview](70_upgrade.md)
