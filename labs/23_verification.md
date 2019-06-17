## 2.3 Verify the Installation

After the completion of the installation, we can verify, if everything is running as expected. Most of the checks have already been done by the playbooks.
First check if the API reachable and all nodes are ready with the right tags.
```
[ec2-user@master0 ~]$ oc get nodes --show-labels
```

Check if all pods are running and if OpenShift could deploy all needed components
```
[ec2-user@master0 ~]$ oc get pods --all-namespaces
```

Check if all pvc are bound and glusterfs runs fine
```
[ec2-user@master0 ~]$ oc get pvc --all-namespaces
```

Check the etcd health status. 
```
[ec2-user@master0 ~]$ sudo -i
[root@master0 ~]# source /etc/etcd/etcd.conf
[root@master0 ~]# etcdctl2 cluster-health
member 16682006866446bb is healthy: got healthy result from https://172.31.45.211:2379
member 5c619e4b51953519 is healthy: got healthy result from https://172.31.44.160:2379
cluster is healthy

[root@master0 ~]# etcdctl2 member list
16682006866446bb: name=master1.user7.lab.openshift.ch peerURLs=https://172.31.45.211:2380 clientURLs=https://172.31.45.211:2379 isLeader=false
5c619e4b51953519: name=master0.user7.lab.openshift.ch peerURLs=https://172.31.44.160:2380 clientURLs=https://172.31.44.160:2379 isLeader=true
```

Create a project, run a build, push/pull from the internal registry and deploy a test application.
```
[ec2-user@master0 ~]$ oc new-project dakota
[ec2-user@master0 ~]$ oc new-app centos/ruby-22-centos7~https://github.com/openshift/ruby-ex.git
[ec2-user@master0 ~]$ oc get pods -w
```
We keep this project so we have at least one pod running on OpenShift. If you decide to create other projects/pods you may delete this project with `oc delete project dakota`.

**End of Lab 2.3**

<p width="100px" align="right"><a href="30_daily_business.md">3. Daily Business →</a></p>

[← back to the Chapter Overview](20_installation.md)
