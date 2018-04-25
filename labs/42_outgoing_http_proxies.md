## Lab 4.2: Outgoing HTTP Proxies

Large corporations often allow internet access only via outgoing HTTP proxies for security reasons.
To use OpenShift Container Platform in such an environment the various OpenShift components and 
the containers that run on the platform need to be configured to use an HTTP proxy. In addition
internal resources must be excluded from access via proxy as outgoing proxies usually only allow
access to external resources. This lab shows how to configure OpenShift Container for outgoing
HTTP proxies using the included Ansible playbooks.
We haven't yet added an outgoing HTTP proxy to our lab environment. Therefore this lab currently doesn't
contain hands-on exercises.


### Configure the Ansible Inventory

The OpenShift Ansible playbooks support three groups of variables for outgoing HTTP proxy configuration.

Configuration for OpenShift components, container runtime, e.g. Docker, and containers running on the platform:

    openshift_http_proxy=<proxy url>
    openshift_https_proxy=<proxy url>
    openshift_no_proxy='<no_proxy list>'

Where `<proxy url>` can take one of the following forms:

    http://proxy.example.org:3128
    http://192.0.2.42:3128
    http://proxyuser:proxypass@proxy.example.org:3128
    http://proxyuser:proxypass@192.0.2.42:3128

In all cases https can be used instead of http, provided this is supported by the proxy.  
`<no_proxy list>` consists of a comma separated list of:
* hostnames, e.g. `my.example.org`
* domains, e.g. `.example.org`
* IP addresses, e.g. `192.0.2.42`

Additionally OpenShift implements support for IP subnets, e.g. `192.0.2.0/24`, in `no_proxy`. However other software, including Docker, does not support such entries and ignores them.

Docker build containers are created directly by Docker with a clean environment, i.e. without the required proxy environment variables.
The following variables tell OpenShift to add `ENV` instructions with the outgoing HTTP proxy configuration to all Docker builds.
This is needed to allow builds to download dependencies from external sources:

    openshift_builddefaults_http_proxy=<proxy url>
    openshift_builddefaults_https_proxy=<proxy url>
    openshift_builddefaults_no_proxy='<no_proxy list>'

Finally an outgoing HTTP proxy can be configured to allow OpenShift builds to check out sources from external Git repositories:

    openshift_builddefaults_git_http_proxy=<proxy url>
    openshift_builddefaults_git_https_proxy=<proxy url>
    openshift_builddefaults_git_no_proxy=<no_proxy list>


### Internal Docker Registry

It's recommended to add the IP address of the internal registry to the `no_proxy`
lists. The IP addressed of the internal registry can be looked up after cluster installation with:

    oc get svc docker-registry -n default -o jsonpath='{.spec.clusterIP}'

For OpenShift Container Platform 3.5 and earlier this is required as the registry is always
accessed via IP address and Docker doesn't support IP subnets in its `no_proxy` list!


### Build Tools

Some build tools use a different mechanism and need additional configuration for accessing outgoing HTTP proxies.


#### Maven

The Java build tool Maven reads the [proxy configuration from its settings.xml](https://maven.apache.org/guides/mini/guide-proxies.html).
Java base images by Red Hat contain [support for configuring Maven's outgoing proxy through environment variables](https://access.redhat.com/documentation/en-us/red_hat_jboss_enterprise_application_platform/7.0/html-single/red_hat_jboss_enterprise_application_platform_for_openshift/#eap_s2i_process).
These environment variables are used by all Red Hat Java base images, not just JBoss ones. They must be added to the BuildConfigs of Maven builds.
To add them to all BuildConfigs on the platform you can use the Ansible inventory variable `openshift_builddefaults_json`,
which must then contain the whole build proxy configuration, i.e. the other `openshift_builddefaults_` variables mentioned earlier are ignored. E.g.:

    openshift_builddefaults_json='
      {"BuildDefaults":{"configuration":{"apiVersion":"v1","env":[
          {"name":"HTTP_PROXY","value":"<proxy url>"},
          {"name":"HTTPS_PROXY","value":"<proxy url>"},
          {"name":"NO_PROXY","value":"<no_proxy list>"},
          {"name":"http_proxy","value":"<proxy url>"},
          {"name":"https_proxy","value":"<proxy url>"},
          {"name":"no_proxy","value":"<no_proxy list>"},
          {"name":"HTTP_PROXY_HOST","value":"<proxy host>"},
          {"name":"HTTP_PROXY_PORT","value":"<proxy port>"},
          {"name":"HTTP_PROXY_USERNAME","value":"<proxy username (optional)>"},
          {"name":"HTTP_PROXY_PASSWORD","value":"<proxy password (optional)>"},
          {"name":"HTTP_PROXY_NONPROXYHOSTS","value":"<no_proxy list>"}],
        "gitHTTPProxy":"<proxy url>",
        "gitHTTPSProxy":"<proxy url>",
        "gitNoProxy":"<no_proxy list>",
        "kind":"BuildDefaultsConfig"}}}'

Note that the value has to be valid JSON.
Also Ansible inventories in INI format do not support line folding, so this has to be a single line.

If you use Java base images other than the ones provided by Red Hat you have to implement your own solution to configure an outgoing HTTP proxy for Maven.


### Apply Outgoing HTTP Proxy Configuration to Cluster

To apply the outgoing HTTP proxy configuration to the cluster you have to run the master and node config playbooks:

    ansible-playbook --tags master,node /usr/share/ansible/openshift-ansible/playbooks/byo/config.yml

---

**End of Lab 4.2**

<p width="100px" align="right"><a href="50_backup_restore.md">5. Backup and Restore →</a></p>

[← back to the Chapter Overview](40_configuration_best_practices.md)
