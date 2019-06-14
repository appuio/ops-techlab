## Lab 5.2: Restore

### Restore a Project

We will now delete the initially created `dakota` project and try to restore it from the backup.
```
[ec2-user@master0 ~]$ oc delete project dakota
```

Check if the project is being deleted
```
[ec2-user@master0 ~]$ oc get project dakota
```

Restore the dakota project from the backup.
```
[ec2-user@master0 ~]$ oc new-project dakota
[ec2-user@master0 ~]$ oc project project-backup
[ec2-user@master0 ~]$ oc debug `oc get pods -o jsonpath='{.items[*].metadata.name}' | awk '{print $1}'`
sh-4.2# tar -xvf /backup/backup-201906131343.tar.gz -C /tmp/
sh-4.2# oc apply -f /tmp/dakota/
```

Start build and push image to registry
```
[ec2-user@master0 ~]$ oc start-build ruby-ex -n dakota
``` 

Check if the pods are coming up again
```
[ec2-user@master0 ~]$ oc get pods -w -n dakota
```

### Restore the etcd Cluster

Official documentation to restore etcd does not work:
https://docs.openshift.com/container-platform/3.11/admin_guide/assembly_restoring-cluster.html#restoring-etcd_admin-restore-cluster

To restore an etcd cluster running in static pods, please follow the following documentation:
https://access.redhat.com/solutions/3885101

### Scaleup the etcd Cluster

We are now running on a single etcd setup. To get HA again, we need to scaleup to at least three etcds.

First add the new etcds host in the Ansible inventory in the (`[new_etcd]`) section and add it to the (`[OSEv3:children]` group).
```
[OSEv3:children]
...
new_etcd

[new_etcd]
master1.user7.lab.openshift.ch
master2.user7.lab.openshift.ch

```

### Scaleup to a HA etcd cluster

Execute the playbook responsible for the etcd scaleup:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/scaleup.yml
```


## Verification and Finalization

Verify your installation now consists of the original cluster plus one new etcd member:
```
[root@master0 ~]# etcdctl2 --cert-file=/etc/etcd/peer.crt \
                           --key-file=/etc/etcd/peer.key \
                           --ca-file=/etc/etcd/ca.crt \
                           --peers="https://master0.user[X].lab.openshift.ch:2379,https://master1.user[X].lab.openshift.ch:2379" \
                           cluster-health
```

Move the now functional etcd members from the group `[new_etcd]` to `[etcd]` in your Ansible inventory at `/etc/ansible/hosts` so the group looks like:
```
...
[etcd]
master0.user[X].lab.openshift.ch
master1.user[X].lab.openshift.ch
master2.user[X].lab.openshift.ch
```

---

**End of Lab 5.2**

<p width="100px" align="right"><a href="60_monitoring_troubleshooting.md">6. Monitoring and Troubleshooting →</a></p>

[← back to the Chapter Overview](50_backup_restore.md)
