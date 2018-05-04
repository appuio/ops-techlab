## Lab 2.1: Create the Ansible Inventory

In this lab, we will verify the Ansible inventory file, so it fits our lab cluster. The Inventory file describes, how the cluster will be built.

Take a look at the prepared inventory file:
```
[ec2-user@master0 ~]$ less /etc/ansible/hosts
```

Download the default example hosts file from the OpenShift GitHub repository and compare it to the prepared inventory for the lab. We will use the default OpenShift 3.7 template, as we will later upgrade to OCP 3.7 and like this we already have the right variables in place.
```
[ec2-user@master0 ~]$ wget https://raw.githubusercontent.com/openshift/openshift-ansible/release-3.7/inventory/byo/hosts.example
[ec2-user@master0 ~]$ less hosts.example
```
---

**End of Lab 2.1**

<p width="100px" align="right"><a href="22_installation.md">2.2 Install OpenShift →</a></p>

[← back to the Chapter Overview](20_installation.md)
