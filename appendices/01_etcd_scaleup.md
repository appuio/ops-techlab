# Appendix 1: etcd Scaleup

This appendix is going to show you how to do a scaleup of etcd hosts.


## Adapt Inventory

Add the new etcd host in the Ansible inventory in the (`[new_etcd]`) section and add it to the (`[OSEv3:children]` group).
```
[OSEv3:children]
...
new_etcd

[new_etcd]
master2.user7.lab.openshift.ch

```

## Scaleup

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

[← back to the labs overview](../README.md)

