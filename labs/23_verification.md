## 2.3 Verify the installation

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

Check the etcd health status. Do not forget to change the *[X]* of *user[X]* with your number.
```
[ec2-user@master0 ~]# sudo etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/origin/master/master.etcd-ca.crt --cert-file=/etc/origin/master/master.etcd-client.crt --key-file=/etc/origin/master/master.etcd-client.key cluster-health
member 92c764a37c90869 is healthy: got healthy result from https://172.31.46.235:2379
cluster is healthy

[ec2-user@master0 ~]# sudo etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/origin/master/master.etcd-ca.crt --cert-file=/etc/origin/master/master.etcd-client.crt --key-file=/etc/origin/master/master.etcd-client.key member list
92c764a37c90869: name=master0.user[X].lab.openshift.ch peerURLs=https://172.31.46.235:2380 clientURLs=https://172.31.46.235:2379 isLeader=true
```

Create a project, run a build, push/pull from the internal registry and deploy a test application.
```
[ec2-user@master0 ~]$ oc new-project dakota
[ec2-user@master0 ~]$ oc new-app centos/ruby-22-centos7~https://github.com/openshift/ruby-ex.git
[ec2-user@master0 ~]$ oc get pods -w
```
We keep this project so we have at least one pod running on OpenShift. If you decide to create other projects/pods you may delete this project with `oc delete project dakota`.

**End of Lab 2.3**

<p width="100px" align="right"><a href="30_daily_business.md">3. Daily business →</a></p>

[← back to the chapter overview](20_installation.md)
