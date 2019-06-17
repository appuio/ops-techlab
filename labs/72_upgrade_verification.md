## Lab 7.3: Verify the Upgrade

Check the version of the `docker` and `atomic-openshift` packages on all nodes and master.
```
[ec2-user@master0 ~]$ ansible all -m shell -a "rpm -qi atomic-openshift | grep -i name -A1"
[ec2-user@master0 ~]$ ansible masters -m shell -a "rpm -qi atomic-openshift-master | grep -i name -A1"
[ec2-user@master0 ~]$ ansible all -m shell -a "rpm -qi atomic-openshift-node | grep -i name -A1"
[ec2-user@master0 ~]$ ansible all -m shell -a "rpm -qi docker | grep -i name -A3"
```

Check the image version of the registry, router, metrics and logging
```
[ec2-user@master0 ~]$ oc get pod -o yaml --all-namespaces | grep -i "image:.*.openshift3"
```

Now we need to verify our installation according to chapter "[2.3 Verify OpenShift Installation](23_verification.md)".


---

**End of Lab 7**

[← back to the Chapter Overview](70_upgrade.md)
