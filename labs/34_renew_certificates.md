## Lab 3.4: Renew Certificates

In this lab we take a look at the OpenShift certificates and how to renew them.

These are the certificates that need to be maintained. For each component there is a playbook provided by Red Hat that will redeploy the certificates:
- masters (API server and controllers)
- etcd  
- nodes
- registry
- router


### Check the Expiration of the Certificates

To check all your certificates, run the playbook `certificate_expiry/easy-mode.yaml`:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/certificate_expiry/easy-mode.yaml
```
The playbook will generate the following reports with the information of each certificate in JSON and HTML format:
```
/tmp/cert-expiry-report.html
/tmp/cert-expiry-report.json
```


### Redeploy etcd Certificates

To get a feeling for the process of redeploying certificates, we will redeploy the etcd certificates.

**Warning:** This will lead to a restart of etcd and master services and consequently cause an outage for a few seconds of the OpenShift API.

First, we check the current etcd certificates creation time:
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Mar 23 12:50:41 2018 GMT
            Not After : Mar 22 12:50:41 2023 GMT
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Mar 23 12:51:34 2018 GMT
            Not After : Mar 22 12:51:35 2020 GMT
```
Note the value for "Validity Not Before:". We will later compare this timestamp with the freshly deployed certificates.

Redeploy the CA certificate of the etcd servers:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-ca.yml
```

Check the current etcd CA certificate creation time:
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Mar 26 06:22:41 2018 GMT
            Not After : Mar 25 06:22:41 2023 GMT
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Mar 23 12:51:34 2018 GMT
            Not After : Mar 22 12:51:35 2020 GMT
```
The etcd CA certificate has been generated, but etcd is still using the old server certificates. We will replace them with the `redeploy-etcd-certificates.yml` playbook.

**Warning:** This will again lead to a restart of etcd and master services and consequently cause an outage for a few seconds of the OpenShift API.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-certificates.yml
```

Check if the server certificate has been replaced:
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
```


### Replace the other main certificates

Use the following playbooks to replace the certificates of the other main components of OpenShift:

**Warning:** Do not yet replace the router certificates with the corresponding playbook as it will break your routers running on OpenShift 3.6. If you want to, replace the router certificates after upgrading to OpenShift 3.7. (Reference: https://bugzilla.redhat.com/show_bug.cgi?id=1490186)

- masters (API server and controllers)
  - /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-master-certificates.yml
- etcd
  - /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-ca.yml
  - /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-certificates.yml
- nodes
  - /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-node-certificates.yml
- registry
  - /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-registry-certificates.yml
- router
  - /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-router-certificates.yml


---

**End of Lab 3.4**

<p width="100px" align="right"><a href="35_add_new_node_and_master.md">3.5 Add New OpenShift Node and Master →</a></p>

[← back to the Chapter Overview](30_daily_business.md)
