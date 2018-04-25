# Appendix 1: Monitoring with Prometheus

This appendix is going to show you how to install Prometheus on OpenShift 3.7.


## Installation

OpenShift 3.7 was the first release to make it possible to install Prometheus via playbooks. So the only thing we are going to have to do is set the Ansible inventory variables and then run the playbook to perform the actual installation.

Add the following part to your Ansible inventory at `/etc/ansible/hosts`:
```
openshift_hosted_prometheus_deploy=true
```

Execute the playbook to install Prometheus:
```
ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-prometheus.yml
```

The playbook creates a new project called `openshift-metrics` and deploys the Prometheus pod consisting of five different containers into it. As soon as the pod is running you will be able to acces it at https://prometheus-openshift-metrics.app[X].lab.openshift.ch/.


---

[← back to the labs overview](../README.md)

