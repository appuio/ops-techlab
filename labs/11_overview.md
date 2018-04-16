## Lab 1.1: Architectural overview

This is the environment we will build and work on. It is deployed on Amazon AWS.

![Lab OpenShift cluster overview](11_ops-techlab.png)

Out lab Platform consist of the following components:
1. Two AWS | Elastic Load Balancer
    1. ELB appX: Used for load balancing to the routers, where the apps are running. (*.appX.lab.openshift.ch)
    1. ELB userX-console: Used for Loadbalancing to the Masters for external access. (console.user[X].lab.openshift.ch)
1. Two OpenShift Masters, which we will scaleup to three masters in a lab.
    1. On the first Master etcd is running.
    1. On all Masters are the master-api and master-controller daemons running.
1. Two Infra-Nodes, where the following components are running.
    1. Container Native Storage
    1. Routers
    1. Metrics
    1. Logging
1. One worker node, which we will scaleup to two nodes in a lab
1. We will use the first master as a Bastion host because of simplicity of the labs. (bastion.user[X].lab.openshift.ch)
    1. (For production use it's recommended to use a separate instance for this.)

---

**End of lab 1.1**

<p width="100px" align="right"><a href="12_access_environment.md">1.2 Access the lab environment →</a></p>

[← back to the chapter overview](10_warmup.md)
