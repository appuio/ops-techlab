## Lab 3.5: Add a new OpenShift node and master

In this lab we will add a new node and a new master to our OpenShift cluster.


### Add a new node

Uncomment the new node (`node3.user...`) in the Ansible inventory and also uncomment the `new_nodes` group in the "[OSEv3:children]" section.
```
[root@master0 ec2-user]# vi /etc/ansible/hosts
...
glusterfs
bastion
#new_masters
new_nodes
...

[new_nodes]
node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}" openshift_schedulable=false
...

```

As in lab 2.2 we need to run an Ansible playbook to prepare the new node for the OpenShift installation. The playbook enables required repositories, installs packages and sets up storage according to the [documented prerequisites](https://docs.openshift.com/container-platform/3.6/install_config/install/host_preparation.html).

Test the ssh connection and run the pre-install playbook:
```
[ec2-user@master0 ~]$ ansible node3.user[X].lab.openshift.ch -m ping
[ec2-user@master0 ~]$ ansible-playbook resource/pre-install.yml --limit=node3.user[X].lab.openshift.ch
```

Now add the new node with the scaleup playbook:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-node/scaleup.yml
```

Check if the node is ready:
```
[ec2-user@master0 ~]$ oc get nodes
NAME                             STATUS                     AGE       VERSION
master0.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
master1.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
node0.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node1.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node2.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node3.user[X].lab.openshift.ch     Ready,SchedulingDisabled   1m        v1.6.1+5115d708d7
```

Enable scheduling for the new node node3, drain another one (e.g. node2) and check if pods are running correctly on the new node. If you don't see any pods on it make sure there is at least one "non-infra-pod" running on your OpenShift cluster.
```
[ec2-user@master0 ~]$ oc adm drain node2.user[X].lab.openshift.ch --ignore-daemonsets --delete-local-data
[ec2-user@master0 ~]$ watch "oc adm manage-node node3.user[X].lab.openshift.ch --list-pods"
```

If everything works as expected, we schedule node2 again:
```
[ec2-user@master0 ~]$ oc adm manage-node node2.user[X].lab.openshift.ch --schedulable
```

Inside the Ansible inventory, we move the new node from the `[new_nodes]` to the `[app_nodes]` group:
```
[root@master0 ~]$ cat /etc/ansible/hosts
...
[nodes]
master0.user[X].lab.openshift.ch openshift_hostname=master0.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
master1.user[X].lab.openshift.ch openshift_hostname=master1.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
node0.user[X].lab.openshift.ch openshift_hostname=node0.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
node1.user[X].lab.openshift.ch openshift_hostname=node1.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
node2.user[X].lab.openshift.ch openshift_hostname=node2.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}"
node3.user[X].lab.openshift.ch openshift_hostname=node3.user[X].lab.openshift.ch openshift_node_labels="{'region': 'main', 'zone': 'default'}"
...

[new_nodes]
#master2.user...

[glusterfs]
...
```

### Add a new master

Uncomment the new master inside the Ansible inventory. It needs to be in both the `[new_nodes]` and the `[new_masters]` groups.
```
[root@master0 ~]# cat /etc/ansible/hosts
...
glusterfs
bastion
new_masters
new_nodes
...
[new_masters]
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
...
[new_nodes]
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'zone': 'default'}" openshift_schedulable=false
...
```

Check if the host is accessible and run the pre-install playbook:
```
[ec2-user@master0 ~]$ ansible master2.user[X].lab.openshift.ch -m ping
[ec2-user@master0 ~]$ ansible-playbook resource/pre-install.yml --limit=master2.user[X].lab.openshift.ch
```

Now we can add the new master:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-master/scaleup.yml
```

Let's check if the node daemon on the new master is ready:
```
[ec2-user@master0 ~]$ oc get nodes
NAME                             STATUS                     AGE       VERSION
master0.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
master1.user[X].lab.openshift.ch   Ready,SchedulingDisabled   6d        v1.6.1+5115d708d7
master2.user[X].lab.openshift.ch   Ready,SchedulingDisabled   10m       v1.6.1+5115d708d7
node0.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node1.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node2.user[X].lab.openshift.ch     Ready                      6d        v1.6.1+5115d708d7
node3.user[X].lab.openshift.ch     Ready                      32m       v1.6.1+5115d708d7
```

Check if the old masters see the new one:
```
[ec2-user@master0 ~]$ curl https://master2.user[X].lab.openshift.ch
{
  "paths": [
    "/api",
    "/api/v1",
    "/apis",
    "/apis/apps",
    "/apis/apps.openshift.io",
    "/apis/apps.openshift.io/v1",
    "/apis/apps/v1beta1",
    "/apis/authentication.k8s.io",
    "/apis/authentication.k8s.io/v1",
    "/apis/authentication.k8s.io/v1beta1",
    "/apis/authorization.k8s.io",
    "/apis/authorization.k8s.io/v1",
    "/apis/authorization.k8s.io/v1beta1",
    "/apis/authorization.openshift.io",
    "/apis/authorization.openshift.io/v1",
    "/apis/autoscaling",
    "/apis/autoscaling/v1",
    "/apis/batch",
    "/apis/batch/v1",
    "/apis/batch/v2alpha1",
    "/apis/build.openshift.io",
    "/apis/build.openshift.io/v1",
    "/apis/certificates.k8s.io",
    "/apis/certificates.k8s.io/v1beta1",
    "/apis/extensions",
    "/apis/extensions/v1beta1",
    "/apis/image.openshift.io",
    "/apis/image.openshift.io/v1",
    "/apis/network.openshift.io",
    "/apis/network.openshift.io/v1",
    "/apis/oauth.openshift.io",
    "/apis/oauth.openshift.io/v1",
    "/apis/policy",
    "/apis/policy/v1beta1",
    "/apis/project.openshift.io",
    "/apis/project.openshift.io/v1",
    "/apis/quota.openshift.io",
    "/apis/quota.openshift.io/v1",
    "/apis/rbac.authorization.k8s.io",
    "/apis/rbac.authorization.k8s.io/v1beta1",
    "/apis/route.openshift.io",
    "/apis/route.openshift.io/v1",
    "/apis/security.openshift.io",
    "/apis/security.openshift.io/v1",
    "/apis/storage.k8s.io",
    "/apis/storage.k8s.io/v1",
    "/apis/storage.k8s.io/v1beta1",
    "/apis/template.openshift.io",
    "/apis/template.openshift.io/v1",
    "/apis/user.openshift.io",
    "/apis/user.openshift.io/v1",
    "/controllers",
    "/healthz",
    "/healthz/ping",
    "/healthz/poststarthook/bootstrap-controller",
    "/healthz/poststarthook/ca-registration",
    "/healthz/ready",
    "/metrics",
    "/oapi",
    "/oapi/v1",
    "/swaggerapi",
    "/version",
    "/version/openshift"
  ]
}
...
```

If everything works as expected, we move the new master from the `[new_masters]` to the `[masters]` group inside the Ansible inventory:
```
[root@master0 ~]# vi /etc/ansible/hosts
[masters]
master0.user[X].lab.openshift.ch
master1.user[X].lab.openshift.ch
master2.user[X].lab.openshift.ch
...
```

This means we now have an empty `[new_nodes]` and `[new_masters]` groups.
```
[root@master0 ~]# cat /etc/ansible/hosts
...
[new_masters]
...
[new_nodes]
```

---

**End of lab 3.5**

<p width="100px" align="right"><a href="40_configuration_best_practices.md">4. Configuration best practices →</a></p>

[← back to the chapter overview](30_daily_business.md)
