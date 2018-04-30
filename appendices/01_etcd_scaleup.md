# Appendix 2: etcd Scaleup

This appendix is going to show you how to do a scaleup of etcd hosts.


## Adapt Inventory

Uncomment the new etcd hosts in the Ansible inventory in the (`[new_etcd]`) section.
```
...
[etcd]
master0.user8.lab.openshift.ch

[new_etcd]
master1.user8.lab.openshift.ch
master2.user8.lab.openshift.ch
...
```

## Scaleup

Execute the playbook responsible for the etcd scaleup:
```
ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-etcd/scaleup.yml
```


## Verification and Finalization

Verify your installation now consists of the original cluster plus one new etcd member:
```
sudo etcdctl -C https://master0.user[X].lab.openshift.ch:2379 --ca-file=/etc/origin/master/master.etcd-ca.crt --cert-file=/etc/origin/master/master.etcd-client.crt --key-file=/etc/origin/master/master.etcd-client.key cluster-health
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

