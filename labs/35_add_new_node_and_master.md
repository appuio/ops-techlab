## Lab 3.5: Add New OpenShift Node and Master

In this lab we will add a new node and a new master to our OpenShift cluster.


### Add a New Node

Uncomment the new node (`app-node1.user...`) in the Ansible inventory and also uncomment the `new_nodes` group in the "[OSEv3:children]" section.
```
[ec2-user@master0 ~]$ sudo vim /etc/ansible/hosts
...
glusterfs
bastion
new_masters
new_nodes
...

[new_nodes]
app-node1.user7.lab.openshift.ch openshift_node_group_name='node-config-compute'
...

```

As in lab 2.2 we need to run an Ansible playbook to prepare the new node for the OpenShift installation. The playbook enables required repositories, installs packages and sets up storage according to the [documented prerequisites](https://docs.openshift.com/container-platform/3.6/install_config/install/host_preparation.html).

Test the ssh connection and run the pre-install playbook:
```
[ec2-user@master0 ~]$ ansible new_nodes[0] -m ping
[ec2-user@master0 ~]$ ansible-playbook resource/prepare_hosts_for_ose.yml --limit=new_nodes[0]
[ec2-user@master0 ~]$ ansible-playbook resource/prepare_docker_storage.yml --limit=new_nodes[0]
```

Now add the new node with the scaleup playbook:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-node/scaleup.yml
```

Check if the node is ready:
```
[ec2-user@master0 ~]$ oc get nodes
NAME                                 STATUS                     AGE       VERSION
app-node0.user2.lab.openshift.ch     Ready                      3h        v1.6.1+5115d708d7
app-node1.user2.lab.openshift.ch     Ready,SchedulingDisabled   4m        v1.6.1+5115d708d7
infra-node0.user2.lab.openshift.ch   Ready                      4h        v1.6.1+5115d708d7
infra-node1.user2.lab.openshift.ch   Ready                      4h        v1.6.1+5115d708d7
infra-node2.user2.lab.openshift.ch   Ready                      4h        v1.6.1+5115d708d7
master0.user2.lab.openshift.ch       Ready,SchedulingDisabled   4h        v1.6.1+5115d708d7
master1.user2.lab.openshift.ch       Ready,SchedulingDisabled   4h        v1.6.1+5115d708d7
```

Enable scheduling for the new node app-node1, drain another one (e.g. app-node0) and check if pods are running correctly on the new node. If you don't see any pods on it make sure there is at least one "non-infra-pod" running on your OpenShift cluster.
```
[ec2-user@master0 ~]$ oc adm manage-node app-node1.user[X].lab.openshift.ch --schedulable
[ec2-user@master0 ~]$ oc adm drain app-node0.user[X].lab.openshift.ch --ignore-daemonsets --delete-local-data
[ec2-user@master0 ~]$ watch "oc adm manage-node app-node1.user[X].lab.openshift.ch --list-pods"
```

If everything works as expected, we schedule app-node0 again:
```
[ec2-user@master0 ~]$ oc adm manage-node app-node0.user[X].lab.openshift.ch --schedulable
```

Inside the Ansible inventory, we move the new node from the `[new_nodes]` to the `[app_nodes]` group:
```
[ec2-user@master0 ~]$ cat /etc/ansible/hosts
...
[app_nodes]
app-node0.user[X].lab.openshift.ch openshift_hostname=app-node0.user[X].lab.openshift.ch openshift_public_hostname=app-node0.user[X].lab.openshift.ch openshift_node_labels="{'region': 'primary', 'zone': 'default'}"
app-node1.user[X].lab.openshift.ch openshift_hostname=app-node1.user[X].lab.openshift.ch openshift_public_hostname=app-node1.user[X].lab.openshift.ch openshift_node_labels="{'region': 'primary', 'zone': 'default'}"
...

[new_nodes]
#master2.user...

[glusterfs]
...
```

### Add a New Master

Uncomment the new master inside the Ansible inventory. It needs to be in both the `[new_nodes]` and the `[new_masters]` groups.
```
[ec2-user@master0 ~]$ cat /etc/ansible/hosts
...
glusterfs
bastion
new_masters
new_nodes
...
[new_masters]
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_public_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}" openshift_schedulable=false
...
[new_nodes]
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_public_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}" openshift_schedulable=false
...
```

Check if the host is accessible and run the pre-install playbook:
```
[ec2-user@master0 ~]$ ansible master2.user[X].lab.openshift.ch -m ping
[ec2-user@master0 ~]$ ansible-playbook resource/prepare_hosts_for_ose.yml --limit=master2.user[X].lab.openshift.ch
[ec2-user@master0 ~]$ ansible-playbook resource/prepare_docker_storage.yml --limit=master2.user[X].lab.openshift.ch
```

Now we can add the new master:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-master/scaleup.yml
```

Let's check if the node daemon on the new master is ready:
```
[ec2-user@master0 ~]$ oc get nodes
NAME                             STATUS                     AGE       VERSION
app-node0.user2.lab.openshift.ch     Ready                      3h        v1.6.1+5115d708d7
app-node1.user2.lab.openshift.ch     Ready                      14m       v1.6.1+5115d708d7
infra-node0.user2.lab.openshift.ch   Ready                      4h        v1.6.1+5115d708d7
infra-node1.user2.lab.openshift.ch   Ready                      4h        v1.6.1+5115d708d7
infra-node2.user2.lab.openshift.ch   Ready                      4h        v1.6.1+5115d708d7
master0.user2.lab.openshift.ch       Ready,SchedulingDisabled   4h        v1.6.1+5115d708d7
master1.user2.lab.openshift.ch       Ready,SchedulingDisabled   4h        v1.6.1+5115d708d7
master2.user2.lab.openshift.ch       Ready,SchedulingDisabled   1m        v1.6.1+5115d708d7
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

If everything worked as expected, we are going to move the new master from the `[new_masters]` to the `[masters]` group inside the Ansible inventory:
```
[ec2-user@master0 ~]$ sudo vim /etc/ansible/hosts
[masters]
master0.user[X].lab.openshift.ch openshift_hostname=master0.user[X].lab.openshift.ch openshift_public_hostname=master0.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
master1.user[X].lab.openshift.ch openshift_hostname=master1.user[X].lab.openshift.ch openshift_public_hostname=master1.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
master2.user[X].lab.openshift.ch openshift_hostname=master2.user[X].lab.openshift.ch openshift_public_hostname=master2.user[X].lab.openshift.ch openshift_node_labels="{'region': 'infra', 'zone': 'default'}"
...
```

This means we now have an empty `[new_nodes]` and `[new_masters]` groups.
```
[ec2-user@master0 ~]$ cat /etc/ansible/hosts
...
[new_masters]
...
[new_nodes]
```


### Fix Logging

The default logging stack on OpenShift mainly consists of Elasticsearch, fluentd and Kibana, where fluentd is a DaemonSet. This means that a fluentd pod is automatically deployed on every node, even if scheduling is disabled for that node. The limiting factor for the deployment of DaemonSet pods is the node selector which is set by default to the label `logging-infra-fluentd=true`. The logging playbook attaches this label to all nodes by default, so if you wanted to prevent the deployment of fluentd on certain hosts you had to add the label `logging-infra-fluentd=false` in the inventory. As you may have seen, we do not specify the label specifically in the inventory, which means:
- Every node gets the `logging-infra-fluentd=true` attached by the logging playbook
- fluentd is deployed on every node

This means the new nodes did not yet get the fluentd label because the logging playbook had only been executed when they were not yet active. We can confirm this by looking at what labels each node has:
```
oc get nodes --show-labels
```

Then we correct it either by executing the logging playbook or by manually labelling the nodes with `oc`. Executing the playbook takes quite some time but we leave this choice to you:
- So either execute the playbook:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-logging.yml
```

- Or label the nodes manually with `oc`:
```
[ec2-user@master0 ~]$ oc label node app-node1.user[X].lab.openshift.ch logging-infra-fluentd=true
[ec2-user@master0 ~]$ oc label node master2.user[X].lab.openshift.ch logging-infra-fluentd=true
```

Confirm that the nodes now have the correct label:
```
oc get nodes --show-labels
```


---

**End of Lab 3.5**

<p width="100px" align="right"><a href="40_configuration_best_practices.md">4. Configuration Best Practices →</a></p>

[← back to the Chapter Overview](30_daily_business.md)
