## Lab 1.1: Architectural overview

This is the environment we will build and work on. It is deployed on Amazon AWS.

![Lab OpenShift cluster overview](../resources/11_ops-techlab.png)

Our lab installation consists of the following components:
1. Two Load Balancers
  1. LB app[X]: Used for load balancing requests to the routers (*.app[X].lab.openshift.ch)
  1. LB user[X]-console: Used for load balancing reqeusts to the master APIs (console.user[X].lab.openshift.ch)
1. Two OpenShift masters, one will be added later
  1. etcd is already installed on all three masters
1. Two infra nodes, where the following components are running:
  1. Container Native Storage (Gluster)
  1. Routers
  1. Metrics
  1. Logging
1. One app node, one will be added later
1. For now, we are going to use the first master as a bastion host (bastion.user[X].lab.openshift.ch)


---

**End of lab 1.1**

<p width="100px" align="right"><a href="12_access_environment.md">1.2 Access the lab environment →</a></p>

[← back to the chapter overview](10_warmup.md)
