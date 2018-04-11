Lab 3.2: Install Openshift Container Platform
============

Lab 3.2.2: Install Openshift
-------------
## Installation of Openshift
In the previous lab we prepared the Ansible inventory to fit our test lab environment. Now we can prepare and run the installation.

Now we run the pre-install.yml playbook. This will do the following:
- Enable Ansible ssh pipelining.
- Attach all needed repositories for the installation of Openshift on all nodes
- Install the prerequisite packages: wget git net-tools bind-utils iptables-services bridge-utils bash-completion kexec-tools sos psacct
- Enable iptables on all nodes
```
[ec2-user@master0 ~]$ ansible-playbook /home/ec2-user/resource/pre-install.yml
```

Run the installation in three steps.
1. Installation of Openshift
Prepare a coffee, this run takes some time.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/config.yml
```

2. Deploying Openshift metrics
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-metrics.yml
```

3. Deploying Openshift logging
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-logging.yml
```

4. Add the cluster-admin role to the "shushu" user.
```
[ec2-user@master0 ~]$ oc adm policy --as system:admin add-cluster-role-to-user cluster-admin shushu
```

5. Now open your browser and access the master API with the user "shushu". Password is documented in the Ansible inventory.
```
https://console.user[X].lab.openshift.ch/console/
```

6. You can download the binary for the client and use it from your local workstation. The binary is available for Linux, macOS and Windows. You can get it here:
```
https://console.user[X].lab.openshift.ch/console/extensions/clients/
```

## Verify Openshift installation
After the completion of the installation, we can verify, if everything is running as expected. Most of the checks are already been done by the playbooks.
First check if the API reachable and all nodes are ready with the right tags.
```
[ec2-user@master0 ~]$ oc get nodes --show-labels
```

Check if all pods are running and if Openshift could deploy all needed components
```
[ec2-user@master0 ~]$ oc get pods --all-namespaces
```

Check if all pvc are bound and glusterfs runs fine
```
[ec2-user@master0 ~]$ oc get pvc --all-namespaces
```

Check the etcd health status (as root user). Do not forget to change the *[X]* of *user[X]* with your number.
```
[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/origin/master/master.etcd-ca.crt --cert-file=/etc/origin/master/master.etcd-client.crt --key-file=/etc/origin/master/master.etcd-client.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://172.31.46.235:2379
cluster is healthy

[root@master0 ~]# etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/origin/master/master.etcd-ca.crt --cert-file=/etc/origin/master/master.etcd-client.crt --key-file=/etc/origin/master/master.etcd-client.key member list
92c764a37c90869: name=master0.user[X].lab.openshift.ch peerURLs=https://172.31.46.235:2380 clientURLs=https://172.31.46.235:2379 isLeader=true
```

Create a project, run a build, push/pull from the internal registry and deploy a test application.
```
[ec2-user@master0 ~]$ oc new-project test
[ec2-user@master0 ~]$ oc new-app centos/ruby-22-centos7~https://github.com/openshift/ruby-ex.git
[ec2-user@master0 ~]$ oc get pods -w
[ec2-user@master0 ~]$ oc delete project test
```

---

**End of Lab 3.2.2**

<p width="100px" align="right"><a href="331_user_management.md">User management →</a></p>

[← back to overview](../README.md)
