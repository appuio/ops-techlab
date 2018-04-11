Lab 3.2: Install Openshift Container Platform
============

Lab 3.2.1: Create Ansible inventory
-------------
In this lab, we will verify the Ansible inventory file, so it fits our lab cluster. The Inventory file describes, how the cluster will be built.
First we will download the default example hosts file from the Openshift Github repository and compare it to the prepared inventory for the lab. We will use the default Openshift 3.7 template, as we will later upgrade to OSE 3.7 and like this we already have the right variables in place.

Login to the first master and compare the Ansible Inventories
```
[ec2-user@master0 ~]$ wget https://raw.githubusercontent.com/openshift/openshift-ansible/release-3.7/inventory/byo/hosts.example
[ec2-user@master0 ~]$ vimdiff /etc/ansible/hosts hosts.example
```
As we can see there are the following differences:
1. [OSEv3:children]
    1. lb, nfs, new_masters and new_nodes are commented out.
    1. glusterfs hostgroup: Deploy Container Native Storage.
1. ansible_ssh_user: Run Ansible playbook as ec2-user.
1. ansible_become: The ec2-user is not in the root group, so we need the ansible_become=yes set.
1. openshift_deployment: Deploy "openshift-enterprise".
1. openshift_release: Deploy Openshift 3.6, then upgrade to 3.7.
1. openshift_master_extensions: Make the oc client available on console
1. openshift_master_htpasswd_users: Create a default user, so we can login after the installation.
1. openshift_master_cluster_hostname: Set the cluster private hostname.
1. openshift_master_cluster_public_hostname: Set the cluster-public hostname.
1. openshift_master_default_subdomain: Set the subdomain for our apps.
1. openshift_hosted_router_replicas: Run at least 2 router pods. They will be running on each of the two infra-node.
1. openshift_hosted_manage_router: Let Openshift manage routers.
1. openshift_hosted_registry_replicas: Run two router pods for fail-over
1. openshift_hosted_registry_storage_kind: Use container native storage for the registry persistent volume.
1. openshift_metrics_install_metrics: Deploy Openshift metrics.
1. openshift_metrics_hawkular_hostname: Define metrics url
1. openshift_logging_install_logging: Deploy Openshift logging.
1. openshift_logging_es_memory_limit: Adjust the memory limit, because the lab environment is not sized as a production environment.
1. openshift_logging_kibana_hostname: Define URL to access logs
1. openshift_master_api_port: Set Port to 443 for master API
1. openshift_master_console_port: Set Port to 443 for master API
1. openshift_pkg_version: Define the exact package version.
1. openshift_set_node_ip: It's recommended to set this setting to avoid CDN DNS issues, if using multiple network interfaces.
1. openshift_master_dynamic_provisioning_enabled: Deploy Container Native Storage.
    1. openshift_storage_glusterfs_namespace
    1. openshift_storage_glusterfs_storageclass_default
    1. openshift_storage_glusterfs_wipe
1. openshift_disable_check: Disable a few checks, because the lab environment is not sized as a production environment.
1. [masters],[etcd],[lb],[nodes],[new_nodes],[new_masters],[glusterfs]: Specify all hosts, that it fits with the environment.

---

**End of Lab 3.2.1**

<p width="100px" align="right"><a href="322_install_openshift.md">Install Openshift →</a></p>

[← back to overview](../README.md)
