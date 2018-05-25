## Lab 4.1: Out of Resource Handling

This lab deals with out of resource handling on OpenShift platforms, most importantly the handling of out-of-memory conditions. Out of resource conditions can occur either on the container level because of resource limits or on the node level because a node runs out of memory as a result of overcommitting.
They are either handled by OpenShift or directly by the kernel.


### Introduction

The following terms and behaviours are crucial in understanding this lab.

Killing a pod or a container are fundamentally different:
* Pods and its containers live on the same node for the duration of their lifetime.
* A pod's restart policy determines whether its containers are restarted after being killed.
* Killed containers always restart on the same node.
* If a pod is killed the configuration of its controller, e.g. ReplicationController, ReplicaSet, Job, ..., determines whether a replacement pod is created.
* Pods without controllers are never replaced after being killed.

An OpenShift node recovers from out of memory conditions by killing containers or pods:
* **Out of Memory (OOM) Killer**: Linux kernel mechanism which kills processes to recover from out of memory conditions.
* **Pod Eviction**: An OpenShift mechanism which kills pods to recover from out of memory conditions.

The order in which containers and pods are killed is determined by their Quality of Service (QoS) class.
The QoS class in turn is defined by resource requests and limits developers configure on their containers.
For more information see [Quality of Service Tiers](https://docs.openshift.com/container-platform/3.6/dev_guide/compute_resources.html#quality-of-service-tiers).


### Out of Memory Killer in Action

To observe how the OOM killer in action create a container which allocates all memory available on the node it runs on:

```
[ec2-user@master0 ~]$ oc new-project out-of-memory
[ec2-user@master0 ~]$ oc create -f https://raw.githubusercontent.com/appuio/ops-techlab/release-3.6/resources/membomb/pod_oom.yaml
```

Wait till the container is up and being killed. `oc get pods -o wide` will then show:
```
NAME              READY     STATUS      RESTARTS   AGE       IP            NODE
membomb-1-z6md2   0/1       OOMKilled   0          7s        10.131.2.24   node4.user8.lab.openshift.ch
```

Run `oc describe pod -l app=membomb` to get more information about the container state which should look like this:
```
State:              Terminated
  Reason:           OOMKilled
  Exit Code:        137
  Started:          Thu, 17 May 2018 10:51:02 +0200
  Finished:         Thu, 17 May 2018 10:51:04 +0200
```

Exit code 137 [indicates](http://tldp.org/LDP/abs/html/exitcodes.html) that the container main process was killed by the `SIGKILL` signal.
With the default `restartPolicy` of `Always` the container would now restart on the same node. For this lab the `restartPolicy`
has been set to `Never` to prevent endless out-of-memory conditions and restarts.

Now log into the OpenShift node the pod ran on and study how the OOM event looks like in the kernel logs.
You can see on which node the pod ran in the output of either the `oc get` or `oc describe` command you just ran.
In this example this would look like:

```
ssh node4.user[X].lab.openshift.ch
journalctl -ke
```

The following lines should be highlighted:

May 17 10:51:04 node4.user8.lab.openshift.ch kernel: Memory cgroup out of memory: Kill process 5806 (python) score 1990 or sacrifice child
May 17 10:51:04 node4.user8.lab.openshift.ch kernel: Killed process 5806 (python) total-vm:7336912kB, anon-rss:5987524kB, file-rss:0kB, shmem-rss:0kB

This log messages indicate that the OOM killer has been invoked because a cgroup memory limit has been exceeded
and that it killed a python process which consumed 5987524kB memory. Cgroup is a kernel mechanism which limits
resource usage of processes.  
Further up in the log you should see a line like the following, followed by usage and limits of the corresponding cgroup hierarchy:

```
May 17 10:51:04 node4.user8.lab.openshift.ch kernel: Task in /kubepods.slice/kubepods-besteffort.slice/kubepods-besteffort-pod6ba0af16_59af_11e8_9a62_0672f11196a0.slice/docker-648ff0b111978161b0ac94fb72a4656ee3f98b8e73f7eb63c5910f5cf8cd9c53.scope killed as a result of limit of /kubepods.slice
```

This message tells you that a limit of the cgroup `kubepods.slice` has been exceeded. That's the cgroup
limiting the resource usage of all container processes on a node, preventing them from using resources
reserved for the kernel and system daemons.  
Note that a container can also be killed by the OOM killer because it reached its own memory limit. In that
case a different cgroup will be listed in the `killed as a result of limit of` line. Everything
else will however look the same.

There are some drawbacks to containers being killed by the out of memory killer:
* Containers are always restarted on the same node, possibly repeating the same out of memory condition over and over again.
* There is no grace period, container processes are immediately killed with SIGKILL.

Because of this OpenShift provides the "Pod Eviction" mechanism to kill and reschedule pods before they trigger
an out of resource condition.


### Pod Eviction

OpenShift offers hard and soft evictions. Hard evictions act immediately when the configured threshold is reached.
Soft evictions allow the threshold to be exceeded for a configurable grace period before taking action.

To observe a pod eviction create a container which allocates memory till it is being evicted:

```
[ec2-user@master0 ~]$ oc create -f https://raw.githubusercontent.com/appuio/ops-techlab/release-3.6/resources/membomb/pod_eviction.yaml
```

Wait till the container gets evicted. Run `oc describe pod -l app=membomb` to see the reason for the eviction:
```
Status:                 Failed
Reason:                 Evicted
Message:                The node was low on resource: memory.
```

After a pod eviction a node is flagged as being under memory pressure for a short time, by default 5 minutes.
Nodes under memory pressure are not considered for scheduling new pods.

### Recommendations

Beginning with OCP 3.6 the memory available for pods on a node is determined by this formula:
```
<allocatable memory> = <node capacity> - <kube-reserved> - <system-reserved> - <hard eviction thresholds>
```

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
OCP 3.6 has a hard memory eviction threshold of 100 MiB preconfigured. No other eviction thresholds are enabled by default.
This is usually to low to trigger pod eviction before the OOM killer hits. We recommend to start with a hard memory eviction
threshold of **500Mi**. If you keep to see lots of OOM killed containers consider increasing the hard eviction threshold or
adding a soft eviction threshold. But remember that hard eviction thresholds are subtracted from the nodes allocatable resources.

You can configure reserves and eviction thresholds in the `openshift_node_kubelet_args` key of your Ansible inventory, e.g.:

```
openshift_node_kubelet_args='{"kube-reserved":["cpu=200m,memory=1G"],"system-reserved":["cpu=200m,memory=1G"],"eviction-hard":["memory.available<500Mi"]}'
```

Then run the config playbook to apply the settings to the cluster.

See [Allocating Node Resources](https://docs.openshift.com/container-platform/3.6/admin_guide/allocating_node_resources.html)
and [Out of Resource Handling](https://docs.openshift.com/container-platform/3.6/admin_guide/out_of_resource_handling.html) for more information.

---

**End of Lab 4.1**

<p width="100px" align="right"><a href="42_outgoing_http_proxies.md">4.2. Outgoing HTTP Proxies →</a></p>

[← back to the Chapter Overview](40_configuration_best_practices.md)
