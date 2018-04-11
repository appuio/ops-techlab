## Lab 3.6.2: Troubleshooting Using Logs

As soon as basic functionality of OpenShift itself is reduced or not working at all, we have to have a closer look at the underlying components' log messages. We find these logs either in the journal on the different servers or in Elasticsearch.

**Note:** If the logging component is not part of the installation, Elasticsearch is not available and therefore the only log location is the journal. Also be aware that Fluentd is responsible for aggregating log messages, but it is possible that Fluentd was not deployed on all OpenShift nodes even though it is a DaemonSet. Check Fluentd's node selector and the node's labels to make sure all logs are aggregated as expected.

**Note:** While it is convenient to use the EFK stack to analyze log messages in a central place, be aware that depending on the problem, relevant log messages might not be received by Elasticsearch (e.g. SDN problems).


### Services Overview

The master usually houses two to three master-specific services:
* `atomic-openshift-master` (in a single-master setup)
* `atomic-openshift-master-api` and `atomic-openshift-master-controllers` (in a multi-master setup)
* `etcd` (usually installed on a master, also possible externally)

The node-specific services can also be found on a master:
* `atomic-openshift-node` (in order for the master to be part of the SDN)
* `docker` 

General services include the following:
* `openvswitch` 
* `dnsmasq`
* `NetworkManager` 


### Service States

Check different service states from the first master using ansible. Check the OpenShift master services first:
```
$ ansible masters -a "systemctl is-active atomic-openshift-master-*"
```

etcd:
```
$ ansible masters -a "systemctl is-active etcd"
```

As we can see, the command `systemctl is-active` only outputs the status but not the service name. That's why we execute above commands for each service separately.

There is also the possibility of checking etcd's health using `etcdctl`:
```
# etcdctl --cert-file=/etc/etcd/peer.crt \
          --key-file=/etc/etcd/peer.key \
          --ca-file=/etc/etcd/ca.crt \
          --peers="https://master0.userX.lab.openshift.ch:2379,\
                   https://master1.userX.lab.openshift.ch:2379,\
                   https://master2.userX.lab.openshift.ch:2379"\
          cluster-health
```

As an etcd cluster needs a quorum to update its state, `etcdctl` will output that the cluster is healthy even if not every member is.

Back to checking services with systemd: Master-specific services only need to be executed on master hosts, so note the change of the host group in the following command.

atomic-openshift-node:
```
$ ansible nodes -a "systemctl is-active atomic-openshift-node"
```

Above command applies to all the other node services (`docker`, `dnsmasq` and `NetworkManager`) with which we get an overall overview of OpenShift-specific service states.

Depending on the outcome of the above commands we have to get a closer look at specific services. This can either be done the conventional way, e.g. the 30 most recent messages for etcd on the first master:

```
$ ansible masters[0] -a "journalctl -u etcd -n 30"
```

Or by searching Elasticsearch: After logging in to https://logging.appX.lab.openshift.ch, make sure you're on Kibana's "Discover" tab. Then choose the `.operations.*` index by clicking on the arrow in the dark-grey box on the left to get a list of all available indices. You can then create search queries such as `systemd.t.SYSTEMD_UNIT:atomic-openshift-node.service` in order to filter for all messages from every running OpenShift node service.

Or if we wanted to filter for error messages we could simply use "error" in the search bar and then by looking at the available fields (in the menu on the left) limit the search results further.

