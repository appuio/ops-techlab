## Lab 2.2: Install OpenShift

In the previous lab we prepared the Ansible inventory to fit our test lab environment. Now we can prepare and run the installation.

Now we run the pre-install.yml playbook. This will do the following:
- Attach all needed repositories for the installation of OpenShift on all nodes
- Install the prerequisite packages: wget git net-tools bind-utils iptables-services bridge-utils bash-completion kexec-tools sos psacct
- Enable Ansible ssh pipelining (performance improvements for Ansible)
```
[ec2-user@master0 ~]$ ansible-playbook /home/ec2-user/resource/pre-install.yml
```

Run the installation
1. Install OpenShift. The `deploy_cluster.yml` playbook takes a while, get a coffee.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/prerequisites.yml 
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/deploy_cluster.yml
```

2. Add the cluster-admin role to the "sheriff" user.
```
[ec2-user@master0 ~]$ oc adm policy --as system:admin add-cluster-role-to-user cluster-admin sheriff
```

3. Now open your browser and access the master API with the user "sheriff":
```
https://console.user[X].lab.openshift.ch/console/
```
Password is documented in the Ansible inventory:
```
grep keepass /home/ec2-user/resource/techlab-inventory
```

4. You can download the client binary from the OpenShift console and use it from your local workstation. The binary is available for Linux, macOS and Windows. (optional)
```
https://console.user[X].lab.openshift.ch/console/command-line
```

---

**End of Lab 2.2**

<p width="100px" align="right"><a href="23_verification.md">2.3 Verify the Installation →</a></p>

[← back to the Chapter Overview](20_installation.md)
