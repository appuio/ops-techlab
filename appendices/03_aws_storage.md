# Appendix 1: Using AWS EBS and EFS Storage

This appendix is going to show you how to use AWS EBS and EFS Storage on OpenShift 3.11.


## Installation
`The external provisioner for AWS EFS on OpenShift Container Platform is a Technology Preview feature.`
https://docs.openshift.com/container-platform/3.11/install_config/provisioners.html

Uncomment the following part in your Ansible inventory at `/etc/ansible/hosts`:
```
openshift_provisioners_install_provisioners=True
openshift_provisioners_efs=True
openshift_cloudprovider_kind=aws
openshift_clusterid=opstechlab
openshift_cloudprovider_aws_access_key= [provided by instructor]
openshift_cloudprovider_aws_secret_key= [provided by instructor]
openshift_provisioners_efs_fsid= [provided by instructor]
openshift_provisioners_efs_region=eu-central-1
openshift_provisioners_efs_aws_access_key_id={{ openshift_cloudprovider_aws_access_key }}
openshift_provisioners_efs_aws_secret_access_key={{ openshift_cloudprovider_aws_secret_key }}
openshift_provisioners_efs_name=
openshift_provisioners_efs_nodeselector=
openshift_provisioners_efs_supplementalgroup=
```

Execute the playbook to install the provisioner:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-master/config.yml
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-master/additional_config.yml
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-provisioners/config.yml
```

### Use EFS Volumes

### Use EBS Volumes

---

[← back to the labs overview](../README.md)

