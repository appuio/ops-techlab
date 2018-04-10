Lab 3.3: Daily business
============

Lab 3.3.3: Renew certificates
-------------
In this lab we take a look at the Openshift certificates and how to renew them.

These are the main certificates, that needs to be maintained. For each component there is playbook provided by Red Hat, that will redeploy the certificates:
-    masters (API server and controllers) 
-    etcd  
-    nodes
-    registry
-    router

## Check the expiration of the certificates
To check all your certificates you can run the playbook "certificate_expiry/easy-mode.yaml" provided from Red Hat. 
```
[ec2-user@master0 ~]$ ansible-playbook -v -i /etc/ansible/hosts /usr/share/ansible/openshift-ansible/playbooks/certificate_expiry/easy-mode.yaml
...
```
It will generate the following files with a dump of all information of each certificate in json and html markup:
```
/tmp/cert-expiry-report.html 
/tmp/cert-expiry-report.json
```

## Redeploy etcd certificates
To get a feeling for the process of redeploying certficates, we will redeploy the ca certificate and the depending certificates of etcd.
WARNING: This will lead to a restart of etcd and master services.

First, we check the current etcd certificates creation time.
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Mar 23 12:50:41 2018 GMT
            Not After : Mar 22 12:50:41 2023 GMT
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/etcd.server.crt -text -noout | grep -i validity -A 2
        Validity
            Not Before: Mar 23 12:51:34 2018 GMT
            Not After : Mar 22 12:51:35 2020 GMT
```
Note down the value for "Validity Not Before:", so you can compare after the new certificates will be deployed.

Run the playbook, that takes care of redeploying the ca certificate of the etcd servers.
```
[ec2-user@master0 ~]$ ansible-playbook -v -i /etc/ansible/hosts /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-ca.yml
...
```

Check the current etcd ca certificate creation time again.
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

You should see now, that a new etcd ca certificate has been generated, but etcd is still using the old server certificate. With the "redeploy-etcd-certificates.yml" playbook from Red Hat, we replace now the server certificate with new ones, signed by the newly created ca certificate.
WARNING: This will lead to a restart of etcd and master services.
```
[ec2-user@master0 ~]$ ansible-playbook -v -i /etc/ansible/hosts /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-certificates.yml
```

Now you can check, if the server certificate is also replaced.
```
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-ca.crt -text -noout | grep -i validity -A 2
[ec2-user@master0 ~]$ sudo openssl x509 -in /etc/origin/master/master.etcd-client.crt -text -noout | grep -i validity -A 2
```

## Replace the other main certificates
You can use the following playbooks to replace the certificates of the other main components on Openshift:
-    masters (API server and controllers)
     -    /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-master-certificates.yml
-    etcd
     -    /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-ca.yml
     -    /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-etcd-certificates.yml
-    nodes
     -    /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-node-certificates.yml
-    registry
     -    /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-registry-certificates.yml
-    router
     -    /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/redeploy-router-certificates.yml
