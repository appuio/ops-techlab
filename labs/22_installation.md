## Lab 2.2: Install OpenShift

In the previous lab we prepared the Ansible inventory to fit our test lab environment. Now we can prepare and run the installation.

To make sure the playbook keeps on running even if there are network issues or something similar, we strongly encourage you to e.g. use `screen` or `tmux`.

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
[ec2-user@master0 ~]$ grep keepass /etc/ansible/hosts
```

4. Deploy the APPUiO openshift-client-distributor. This provides the correct oc client in a Pod and can then be obtained via the OpenShift GUI. For this to work, the Masters must have the package `atomic-openshift-clients-redistributable` installed. In addition the variable `openshift_web_console_extension_script_urls` must be defined in the inventory.
```
[ec2-user@master0 ~]$ grep openshift_web_console_extension_script_urls /etc/ansible/hosts
openshift_web_console_extension_script_urls=["https://client.app1.lab.openshift.ch/cli-download-customization.js"]
[ec2-user@master0 ~]$ ansible masters -m shell -a "rpm -qi atomic-openshift-clients-redistributable"
```

Deploy the openshift-client-distributor.
```
[ec2-user@master0 ~]$ sudo yum install python-openshift
[ec2-user@master0 ~]$ git clone https://github.com/appuio/openshift-client-distributor
[ec2-user@master0 ~]$ cd openshift-client-distributor
[ec2-user@master0 ~]$ ansible-playbook playbook.yml -e 'openshift_client_distributor_hostname=client.app[X].lab.openshift.ch'
```

5. You can now download the client binary and use it from your local workstation. The binary is available for Linux, macOS and Windows. (optional)
```
https://console.user[X].lab.openshift.ch/console/command-line
```

---

**End of Lab 2.2**

<p width="100px" align="right"><a href="23_verification.md">2.3 Verify the Installation →</a></p>

[← back to the Chapter Overview](20_installation.md)
