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
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-checks/certificate_expiry/easy-mode.yaml
```
The playbook will generate the following reports with the information of each certificate in JSON and HTML format:
```
grep -A2 summary $HOME/cert-expiry-report*.json
$HOME/cert-expiry-report*.html
```


### Redeploy etcd Certificates

To get a feeling for the process of redeploying certificates, we will redeploy the etcd certificates.

**Warning:** This will lead to a restart of etcd and master services and consequently cause an outage for a few seconds of the OpenShift API.

First, we check the current etcd certificates creation time:
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Jun  4 15:45:00 2019 GMT
            Not After : Jun  2 15:45:00 2024 GMT

[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Jun  4 15:45:00 2019 GMT
            Not After : Jun  2 15:45:00 2024 GMT

```
Note the value for "Validity Not Before:". We will later compare this timestamp with the freshly deployed certificates.

Redeploy the CA certificate of the etcd servers:
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/redeploy-ca.yml
```

Check the current etcd CA certificate creation time:
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Jun  6 12:58:04 2019 GMT
            Not After : Jun  4 12:58:04 2024 GMT
            
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Jun  4 15:45:00 2019 GMT
            Not After : Jun  2 15:45:00 2024 GMT
```
The etcd CA certificate has been generated, but etcd is still using the old server certificates. We will replace them with the `redeploy-etcd-certificates.yml` playbook.

**Warning:** This will again lead to a restart of etcd and master services and consequently cause an outage for a few seconds of the OpenShift API.
```
[ec2-user@master0 ~]$ ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/redeploy-certificates.yml
```

Check if the server certificate has been replaced:
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
       Validity
            Not Before: Jun  6 12:58:04 2019 GMT
            Not After : Jun  4 12:58:04 2024 GMT

[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Jun  6 13:28:36 2019 GMT
            Not After : Jun  4 13:28:36 2024 GMT
```
### Redeploy nodes Certificates

1. Create a new bootstrap.kubeconfig for nodes (MASTER nodes will just copy admin.kubeconfig):"
```
[ec2-user@master0 ~]$ sudo oc serviceaccounts create-kubeconfig node-bootstrapper -n openshift-infra --config /etc/origin/master/admin.kubeconfig > /tmp/bootstrap.kubeconfig
```

2. Distribute ~/bootstrap.kubeconfig from step 1 to infra and compute nodes replacing /etc/origin/node/bootstrap.kubeconfig
```
[ec2-user@master0 ~]$ ansible nodes -m copy -a 'src=/tmp/bootstrap.kubeconfig dest=/etc/origin/node/bootstrap.kubeconfig'
```

3. Move node.kubeconfig and client-ca.crt. These will get recreated when the node service is restarted:
```
[ec2-user@master0 ~]$ ansible nodes -m shell -a 'mv /etc/origin/node/client-ca.crt{,.old}'
[ec2-user@master0 ~]$ ansible nodes -m shell -a 'mv /etc/origin/node/node.kubeconfig{,.old}'
```
4. Remove contents of /etc/origin/node/certificates/ on app-/infra-nodes:
```
[ec2-user@master0 ~]$ ansible nodes -m shell -a 'rm -rf  /etc/origin/node/certificates' --limit 'nodes:!master*'
```
5. Restart node service on app-/infra-nodes:
:warning: restart atomic-openshift-node will fail, until CSR's are approved! Approve (Task 6) the CSR's and restart the Services again.
```
[ec2-user@master0 ~]$ ansible nodes -m service -a "name=atomic-openshift-node state=restarted" --limit 'nodes:!master*'
```
6. Approve CSRs, 2 should be approved for each node:
```
[ec2-user@master0 ~]$ oc get csr -o name | xargs oc adm certificate approve
```
7. Check if the app-/infra-nodes are READY:
```
[ec2-user@master0 ~]$ oc get node
[ec2-user@master0 ~]$ for i in `oc get nodes -o jsonpath=$'{range .items[*]}{.metadata.name}\n{end}'`; do oc get --raw /api/v1/nodes/$i/proxy/healthz; echo -e "\t$i"; done
```
8. Remove contents of /etc/origin/node/certificates/ on master-nodes:
```
[ec2-user@master0 ~]$ ansible masters -m shell -a 'rm -rf  /etc/origin/node/certificates' 
```
9. Restart node service on master-nodes:
```
[ec2-user@master0 ~]$ ansible masters -m service -a "name=atomic-openshift-node state=restarted" 
```
10. Approve CSRs, 2 should be approved for each node:
```
[ec2-user@master0 ~]$ oc get csr -o name | xargs oc adm certificate approve
```
11. Check if the master-nodes are READY:
```
[ec2-user@master0 ~]$ oc get node
[ec2-user@master0 ~]$ for i in `oc get nodes -o jsonpath=$'{range .items[*]}{.metadata.name}\n{end}' | grep master`; do oc get --raw /api/v1/nodes/$i/proxy/healthz; echo -e "\t$i"; done
```


### Replace the other main certificates

Use the following playbooks to replace the certificates of the other main components of OpenShift:

**Warning:** Do not yet replace the router certificates with the corresponding playbook as it will break your routers running on OpenShift 3.6. If you want to, replace the router certificates after upgrading to OpenShift 3.7. (Reference: https://bugzilla.redhat.com/show_bug.cgi?id=1490186)

- masters (API server and controllers)
  - /usr/share/ansible/openshift-ansible/playbooks/openshift-master/redeploy-certificates.yml
  
- etcd
  - /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/redeploy-ca.yml
  - /usr/share/ansible/openshift-ansible/playbooks/openshift-etcd/redeploy-certificates.yml
  
- registry
  - /usr/share/ansible/openshift-ansible/playbooks/openshift-hosted/redeploy-registry-certificates.yml
  
- router
  - /usr/share/ansible/openshift-ansible/playbooks/openshift-hosted/redeploy-router-certificates.yml
  
  **Warning:** The documented redeploy-certificates.yml for Nodes doesn't exists anymore! (since 3.10) 
  This is already reported: Red Hat Bugzilla – Bug 1635251. 
  Red Hat provided this KCS: https://access.redhat.com/solutions/3782361
  
- nodes (manual steps needed!)
---

**End of Lab 3.4**

<p width="100px" align="right"><a href="35_add_new_node_and_master.md">3.5 Add New OpenShift Node and Master →</a></p>

[← back to the Chapter Overview](30_daily_business.md)
