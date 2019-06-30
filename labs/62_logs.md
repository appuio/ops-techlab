## Lab 6.2: Troubleshooting Using Logs

As soon as basic functionality of OpenShift itself is reduced or not working at all, we have to have a closer look at the underlying components' log messages. We find these logs either in the journal on the different servers or in Elasticsearch.

**Note:** If the logging component is not part of the installation, Elasticsearch is not available and therefore the only log location is the journal. Also be aware that Fluentd is responsible for aggregating log messages, but it is possible that Fluentd was not deployed on all OpenShift nodes even though it is a DaemonSet. Check Fluentd's node selector and the node's labels to make sure all logs are aggregated as expected.

**Note:** While it is convenient to use the EFK stack to analyze log messages in a central place, be aware that depending on the problem, relevant log messages might not be received by Elasticsearch (e.g. SDN problems).


### OpenShift Components Overview

The master usually houses three master-specific containers:
* `master-api` in OpenShift project `kube-system`
* `master-controllers` in OpenShift project `kube-system`
* `master-etcd` in OpenShift project `kube-system` (usually installed on all masters, also possible externally)

The node-specific containers can also be found on a master:
* `sync` in OpenShift project `openshift-node`
* `sdn` and `ovs` in OpenShift project `openshift-sdn`

The node-specific services can also be found on a master:
* `atomic-openshift-node` (in order for the master to be part of the SDN)
* `docker`

General services include the following:
* `dnsmasq`
* `NetworkManager`
* `firewalld`


### Service States

Check etcd and master states from the first master using ansible. Check the OpenShift master container first:
```
[ec2-user@master0 ~]$ oc get pods -n kube-system -o wide
NAME                                                READY     STATUS    RESTARTS   AGE       IP              NODE                             NOMINATED NODE
master-api-master0.user7.lab.openshift.ch           1/1       Running   9          1d        172.31.44.160   master0.user7.lab.openshift.ch   <none>
master-api-master1.user7.lab.openshift.ch           1/1       Running   7          1d        172.31.45.211   master1.user7.lab.openshift.ch   <none>
master-api-master2.user7.lab.openshift.ch           1/1       Running   0          4m        172.31.35.148   master2.user7.lab.openshift.ch   <none>
master-controllers-master0.user7.lab.openshift.ch   1/1       Running   7          1d        172.31.44.160   master0.user7.lab.openshift.ch   <none>
master-controllers-master1.user7.lab.openshift.ch   1/1       Running   6          1d        172.31.45.211   master1.user7.lab.openshift.ch   <none>
master-controllers-master2.user7.lab.openshift.ch   1/1       Running   0          4m        172.31.35.148   master2.user7.lab.openshift.ch   <none>
master-etcd-master0.user7.lab.openshift.ch          1/1       Running   6          1d        172.31.44.160   master0.user7.lab.openshift.ch   <none>
master-etcd-master1.user7.lab.openshift.ch          1/1       Running   4          1d        172.31.45.211   master1.user7.lab.openshift.ch   <none>
```

Depending on the outcome of the above commands we have to get a closer look at specific container. This can either be done the conventional way, e.g. the 30 most recent messages for etcd on the first master:

```
[ec2-user@master0 ~]$ oc logs master-etcd-master0.user7.lab.openshift.ch -n kube-system --tail=30
```

There is also the possibility of checking etcd's health using `etcdctl`:
```
[root@master0 ~]# etcdctl2 --cert-file=/etc/etcd/peer.crt \
                           --key-file=/etc/etcd/peer.key \
                           --ca-file=/etc/etcd/ca.crt \
                           --peers="https://master0.user[X].lab.openshift.ch:2379,https://master1.user[X].lab.openshift.ch:2379" \
                           cluster-health
```

As an etcd cluster needs a quorum to update its state, `etcdctl` will output that the cluster is healthy even if not every member is.

Back to checking services with systemd: Master-specific services only need to be executed on master hosts, so note the change of the host group in the following command.

atomic-openshift-node:
```
[ec2-user@master0 ~]$ ansible nodes -a "systemctl is-active atomic-openshift-node"
```

Above command applies to all the other node services (`docker`, `dnsmasq` and `NetworkManager`) with which we get an overall overview of OpenShift-specific service states.

Depending on the outcome of the above commands we have to get a closer look at specific services. This can either be done the conventional way, e.g. the 30 most recent messages for atomic-openshift-node on the first master:

```
[ec2-user@master0 ~]$ ansible masters[0] -a "journalctl -u atomic-openshift-node -n 30"
```

Or by searching Elasticsearch: After logging in to https://logging.app[X].lab.openshift.ch, make sure you're on Kibana's "Discover" tab. Then choose the `.operations.*` index by clicking on the arrow in the dark-grey box on the left to get a list of all available indices. You can then create search queries such as `systemd.t.SYSTEMD_UNIT:atomic-openshift-node.service` in order to filter for all messages from every running OpenShift node service.

Or if we wanted to filter for error messages we could simply use "error" in the search bar and then by looking at the available fields (in the menu on the left) limit the search results further.

---

**End of Lab 6.2**

<p width="100px" align="right"><a href="70_upgrade.md">Upgrade OpenShift from 3.11.88 to 3.11.104 →</a></p>

[← back to the Chapter Overview](60_monitoring_troubleshooting.md)
