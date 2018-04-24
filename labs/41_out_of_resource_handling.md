## Lab 4.1: Out of resource handling

This lab deals with out of resource handling on OpenShift platforms, most importantly the handling of out-of-memory conditions. Out of resource conditions can occur either on the container level because of resource limits or on the node level because a node runs out of memory as a result of overcommitting.
They are either handled by OpenShift or directly by the kernel.


### Introduction

The following terms and behaviours are crucial in understanding this lab.

Killing a pod or a container are fundamentally different:
* Pods and its containers live on the same node for the duration of their lifetime.
* A pod's restart policy determines whether its containers are restarted after beeing killed.
* Killed containers always restart on the same node.
* If a pod is killed the configuration of its controller, e.g. ReplicationController, ReplicaSet, Job, ..., determines whether a replacement pod is created.
* Pods without controllers are never replaced after beeing killed.

An OpenShift node recovers from out of memory conditions by killing containers or pods:
* **Out of Memory (OOM) Killer**: Linux kernel mechanism which kills processes to recover from out of memory conditions.
* **Pod Eviction**: An OpenShift mechanism which kills pods to recover from out of memory conditions.

The order in which containers and pods are killed is determined by their Quality of Service (QoS) class.
The QoS class in turn is defined by resource requests and limits developers configure on their containers.
For more information see [Quality of Service Tiers](https://docs.openshift.com/container-platform/3.6/dev_guide/compute_resources.html#quality-of-service-tiers).


### Out of memory killer in action

Create a container which allocates memory till it's being killed.

    oc new-project out-of-memory
    oc create -f https://raw.githubusercontent.com/appuio/ops-techlab/release-3.6/resources/membomb/pod_membomb.yaml

Wait till the container is up and being killed. `oc get pods` will then show:

    NAME              READY     STATUS      RESTARTS   AGE
    membomb-1-3gcjg   0/1       OOMKilled   0          31s

Run `oc describe pod -l app=membomb` to get more information about the container state which should look like this:

    State:              Terminated
      Reason:           OOMKilled
      Exit Code:        137
      Started:          Sun, 22 Apr 2018 15:38:22 +0200
      Finished:         Sun, 22 Apr 2018 15:38:48 +0200

Exit code 137 [indicates](http://tldp.org/LDP/abs/html/exitcodes.html) that the container main process was killed by the `SIGKILL` signal.
With the default `restartPolicy` of `Always` the container would now restart on the same node. For this lab the `restartPolicy`
has been set to `Never` to prevent endless out-of-memory conditions and restarts. Note that a pod can also be killed by the OOM killer
because it reached its own memory limit.

There are some drawbacks to containers beeing killed by the out of memory killer:
* Containers are always restarted on the same node, possibly repeating the same out of memory condition over and over again.
* There is no grace period, container processes are immediately killed with SIGKILL.

Because of this OpenShift provides the "Pod Eviction" mechanism to kill and reschedule pods before they trigger
an out of resource condition.


### Pod eviction

OpenShift offers hard and soft evictions. Hard evictions act immediately when the configured threshold is reached.
Soft evictions allow the threshold to be exceeded for a configurable grace period before taking action.

OCP 3.6 has a hard memory eviction threshold of 100 MiB preconfigured. No other eviction thresholds are enabled by default.
This is usually to low to trigger pod eviction before the OOM killer hits, as seen in the previous exercise. So we now increase this threshold to 500 MiB and enable graceful
shutdown of evicted pods.

Usually you would configure pod eviction in the `openshift_node_kubelet_args` key of your Ansible inventory. However since the config playbook that applies the configuration to the cluster takes about 10 minutes to run on OCP 3.6 we apply the configuration directly to the nodes in this lab.

For your `node2` and `node3` host enhance `kubeletArguments` in `/etc/origin/node/node-config.yaml` as follows: 

```yaml
kubeletArguments:
  eviction-hard:
  - memory.available<500Mi
  eviction-max-pod-grace-period:
  - '120'
```

The `eviction-max-pod-grace-period` setting enables graceful shutdown of evicted pods and
limits the grace period specified in each pod to a maximum value. The containers
main processes in the pod first receive a **SIGTERM** signal, giving them a chance to shut down cleanly. If they are still running after the grace period they are killed with **SIGKILL**.

Then restart the OpenShift node service on our `node2` and `node3` hosts:

    systemctl restart atomic-openshift-node

Now run the `membomb` pod again:

    oc create -f https://raw.githubusercontent.com/appuio/ops-techlab/release-3.6/resources/membomb/pod_membomb.yaml

Wait till the container gets evicted. Run `oc describe pod -l app=membomb` to see the reason for the eviction:

    Status:                 Failed
    Reason:                 Evicted
    Message:                The node was low on resource: memory.

After a pod eviction a node is flagged as beeing under memory pressure for a short time, by default 5 minutes.
Nodes under memory pressure are not considered for scheduling new pods.


### Recommendations

Beginning with OCP 3.6 the memory available for pods on a node is determined by this formula:

    <allocatable memory> = <node capacity> - <kube-reserved> - <system-reserved> - <hard eviction thresholds>

Where
* `<node capacity>` is the memory (RAM) of a node.
* `<kube-reserved>` is an option of the OpenShift node service (kubelet), specifying how much memory to reserve for OpenShift node components.
* `<system-reserved>` is an option of the OpenShift node service (kubelet), specifying how much memory to reserve for the kernel and system daemons.

Also beginning with OCP 3.6 the OOM killer is now triggered when the total memory consumed by all pods on a node exceeds the
allocatable memory, even when there's still memory available on the node. You can view the amount of allocatable memory on all
nodes by running `oc describe nodes`.

For stable operations we recommend to reserve about **10%** of the nodes memory for the kernel, system daemons and node components 
with the `kube-reserved` and `system-reserved` parameters. More memory may need to be reserved if you run additional system
daemons for monitoring, backup, etc. on nodes.
Additionally start with a hard memory eviction threshold of **500Mi** as shown in the exercise. If you keep to see lots
of OOM killed containers consider increasing the hard eviction threshold or adding a soft eviction threshold.
But remember that hard eviction thresholds are subtracted from the nodes allocatable resources.

See [Allocating Node Resources](https://docs.openshift.com/container-platform/3.6/admin_guide/allocating_node_resources.html)
and [Out of Resource Handling](https://docs.openshift.com/container-platform/3.6/admin_guide/out_of_resource_handling.html) for more information.

---

**End of lab 4.1**

<p width="100px" align="right"><a href="42_outgoing_http_proxies.md">4.2. Outgoing HTTP proxies →</a></p>

[← back to the chapter overview](40_configuration_best_practices.md)
