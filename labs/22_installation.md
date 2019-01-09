## Lab 2.2: Install OpenShift

In the previous lab we prepared the Ansible inventory to fit our test lab environment. Now we can prepare and run the installation.

To make shure the Playbook finishes, even there are Networkissues we strongly encourage you to use `screen`, `tmux` or a similar tool.

Now we run the prepare_hosts_for_ose.yml playbook. This will do the following:
- Install the prerequisite packages: wget git net-tools bind-utils iptables-services bridge-utils bash-completion kexec-tools sos psacct
- Enable Ansible ssh pipelining (performance improvements for Ansible)
- Set timezone
- Ensure hostname is preserved in cloud-init
- Set default passwords
- Install oc clients for various platforms on all master

```
[ec2-user@master0 ~]$ ansible-playbook /home/ec2-user/resource/prepare_hosts_for_ose.yml
```

Run the installation
1. Install OpenShift. This takes a while, get a coffee.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/config.yml
```

2. Deploy the OpenShift metrics
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-metrics.yml
```

3. Deploy the OpenShift logging
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-logging.yml
```

4. Add the cluster-admin role to the "sheriff" user.
```
[ec2-user@master0 ~]$ oc adm policy --as system:admin add-cluster-role-to-user cluster-admin sheriff
```

5. Now open your browser and access the master API with the user "sheriff". Password is documented in the Ansible inventory.
```
https://console.user[X].lab.openshift.ch/console/
```

6. You can download the client binary and use it from your local workstation. The binary is available for Linux, macOS and Windows. (optional)
```
https://console.user[X].lab.openshift.ch/console/extensions/clients/
```

---

**End of Lab 2.2**

<p width="100px" align="right"><a href="23_verification.md">2.3 Verify the Installation →</a></p>

[← back to the Chapter Overview](20_installation.md)
