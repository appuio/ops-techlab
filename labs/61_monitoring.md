## Lab 6.1: Monitoring

OpenShift monitoring can be categorized into three different categories which each try to answer their own question:
1. Is our cluster in an operational state right now?
2. Will our cluster remain in an operational state in the near future?
3. Does our cluster have enough capacity to run all pods?


### Is Our Cluster in an Operational State at the Moment?

In order to answer this first question, we check the state of different vital components:
* Masters
* etcd
* Routers
* Apps

**Masters** expose health information on an HTTP endpoint at https://`openshift_master_cluster_public_hostname`:`openshift_master_api_port`/healthz that can be checked for a 200 status code. On one hand, this endpoint can be used as a health indicator in a loadbalancer configuration, on the other hand we can use it ourselves for monitoring or troubleshooting purposes.

Check the masters' health state with a HTTP request:
```
$ curl -v https://console.user[X].lab.openshift.ch/healthz
```

As long as the response is a 200 status code at least one of the masters is still working and the API is accessible via Load Balancer (if there is one).

**etcd** also exposes a similar health endpoint at https://`openshift_master_cluster_public_hostname`:2379/health, though it is only accessible using the client certificate and corresponding key stored on the masters at `/etc/origin/master/master.etcd-client.crt` and `/etc/origin/master/master.etcd-client.key`.
```
$ sudo curl --cacert /etc/origin/master/master.etcd-ca.crt --cert /etc/origin/master/master.etcd-client.crt --key /etc/origin/master/master.etcd-client.key https://master0.user[X].lab.openshift.ch:2379/health
```

The **HAProxy router pods** are responsible for getting application traffic into OpenShift. Similar to the masters, HAProxy also exposes a /healthz endpoint on port 1936 which can be checked with e.g.:
```
$ curl -v http://router.app[X].lab.openshift.ch:1936/healthz
```

Using the wildcard domain to access a router's health page results in a positive answer if at least one router is up and running and that's all we want to know right now.

**Note:** Port 1936 is not open by default, so it has to be opened at least for those nodes running the router pods. This can be achieved e.g. by setting the ansible variable `openshift_node_open_ports` (at least as of OpenShift version 3.7 or later).

**Apps** running on OpenShift should of course be (end-to-end) monitored as well, however, we are not interested in a single application per se. We want to know if all applications of a group of monitored applications do not respond. The more applications not responding the more probable a platform-wide problem is the cause.


### Will our Cluster Remain in an Operational State in the Near Future?

The second category is based on a wider array of checks. It includes checks that take a more "classic" approach such as storage monitoring, but also includes above checks to find out if single cluster members are not healthy.

First, let's look at how to use above checks to answer this second question.

The health endpoint exposed by **masters** was accessed via load balancer in the first category in order to find out if the API is generally available. This time however we want to find out if at least one of the master APIs is unavailable, even if there still are some that are accessible. So we check every single master endpoint directly instead of via load balancer:
```
$ for i in {0..2}; do curl -v https://master${i}.user[X].lab.openshift.ch/healthz; done
```

The **etcd** check above is already run against single members of the cluster and can therefore be applied here in the exact same form. The difference only is that we want to make sure every single member is running, not just the number needed to have quorum.

The approach used for the masters also applies to the **HAProxy routers**. A router pod is effectively listening on the node's interface it is running on. So instead of connecting via load balancer, we use the nodes' IP addresses the router pods are running on. In our case, these are nodes 0 and 1:
```
$ for i in {0..2}; do curl -v http://infra-node${i}.user[X].lab.openshift.ch:1936/healthz; done
```

As already mentioned, finding out if our cluster will remain in an operational state in the near future also includes some better known checks we could call a more conventional **components monitoring**.

Next to the usual monitoring of storage per partition/logical volume, there's one logical volume on each node of special interest to us: the **Docker storage**. The Docker storage contains images and container filesystems of running containers. Monitoring the available space of this logical volume is important in order to tune garbage collection. Garbage collection is done by the **kubelets** running on each node. The available garbage collection kubelet arguments can be found in the [official documentation](https://docs.openshift.com/container-platform/3.7/admin_guide/garbage_collection.html).

Speaking of garbage collection, there's another component that needs frequent garbage collection: the registry. Contrary to the Docker storage on each node, OpenShift only provides a command to prune the registry but does not offer a means to execute it on a regular basis. Until it does, setup the [appuio-pruner](https://github.com/appuio/appuio-pruner) as described in its README.


### Does our Cluster Have Enough Capacity to Run All Pods?

Besides the obvious components that need monitoring like CPU, memory and storage, this third question is tightly coupled with requests and limits we looked at in [chapter 4](41_out_of_resource_handling.md).

But let's first get an overview of available resources using tools you might not have heard about before. One such tool is [Cockpit](http://cockpit-project.org/). Cockpit aims to ease administration tasks of Linux servers by making some basic tasks available via web interface. It is installed by default on every master by the OpenShift Ansible playbooks and listens on port 9090. We don't want to expose the web interface to the internet though, so we are going to use SSH port forwarding to access it:
```
$ ssh ec2-user@bastion.user[X].lab.openshift.ch -L 9090:localhost:9090
```

After the SSH tunnel has been established, open http://localhost:9090 in your browser and log in using user `ec2-user` and the password provided by the instructor. Explore the different tabs and sections of the web interface.

Another possibility to get a quick overview of used and available resources is the [kube-ops-view](https://github.com/hjacobs/kube-ops-view) project. Install it on your OpenShift cluster:
```
oc new-project ocp-ops-view
oc create sa kube-ops-view
oc adm policy add-scc-to-user anyuid -z kube-ops-view
oc adm policy add-cluster-role-to-user cluster-admin system:serviceaccount:ocp-ops-view:kube-ops-view
oc apply -f https://raw.githubusercontent.com/raffaelespazzoli/kube-ops-view/ocp/deploy-openshift/kube-ops-view.yaml
oc expose svc kube-ops-view
oc get route | grep kube-ops-view | awk '{print $2}'
```

The design takes some getting used to, but at least the browser zoom can help with the small size.

The information about kube-ops-view as well as its installation instructions are actually from a [blog post series](https://blog.openshift.com/full-cluster-capacity-management-monitoring-openshift/) from Red Hat that does a very good job at explaining the different relations and possibilities to finding an answer to our question about capacity.

These two tools provide a quick look at resource availability. Implementing a mature, enterprise-grade monitoring of OpenShift resources depends on what tools are available already in an IT environment and would go beyond the scope and length of this techlab, but the referred blog post series certainly is a good start.


---

**End of Lab 6.1**

<p width="100px" align="right"><a href="62_logs.md">6.2 Troubleshooting Using Logs →</a></p>

[← back to the Chapter Overview](60_monitoring_troubleshooting.md)
