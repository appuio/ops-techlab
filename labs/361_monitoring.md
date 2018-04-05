## Lab 3.6.1: Monitoring

OpenShift monitoring can be categorized into three different categories which each try to answer their own question:
1. Is our cluster in an operational state right now?
2. Will our cluster remain in an operational state in the near future?
3. Does our cluster have enough capacity to run all pods?


### Is our cluster in an operational state at the moment?

In order to answer the first question, we check the state of different vital components:
* Masters
* etcd
* Routers

Masters expose health information on an HTTP endpoint at https://`openshift_master_cluster_public_hostname`:`openshift_master_api_port`/healthz that can be checked for a 200 status code. On one hand, this endpoint can be used as a health indicator in a loadbalancer configuration, on the other hand we can use it ourselves for monitoring or troubleshooting purposes.

Check the masters' health state with a HTTP request:
```
$ curl -v https://console.userX.lab.openshift.ch/healthz
```

As long as the response is a 200 status code at least one of the masters is still working and the API is accessible via Load Balancer (if there is one).

etcd also exposes a similar health endpoint at https://`openshift_master_cluster_public_hostname`:2379/health, though it is only accessible using the client certificate and corresponding key stored on the masters at `/etc/origin/master/master.etcd-client.crt` and `/etc/origin/master/master.etcd-client.key`.


### Will our cluster remain in an operational state in the near future?



### Does our cluster have enough capacity to run all pods?

