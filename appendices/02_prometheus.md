# Appendix 1: Monitoring with Prometheus

This appendix is going to show you how to install Prometheus on OpenShift 3.7.


## Installation

OpenShift 3.7 was the first release to make it possible to install Prometheus via playbooks. We set the Ansible inventory variables, run the playbook to perform the actual installation and add the following components to the installation:
- Monitor router endpoints
- Deploy node-exporter DaemonSet
- Deploy kube-state-metrics

Uncomment the following part in your Ansible inventory at `/etc/ansible/hosts`:
```
openshift_hosted_prometheus_deploy=true
openshift_prometheus_node_selector={"region":"infra"}
openshift_prometheus_additional_rules_file=/usr/share/ansible/prometheus/prometheus_configmap_rules.yaml
```

Execute the playbook to install Prometheus:
```
ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/openshift-cluster/openshift-prometheus.yml
```

### Monitor OpenShift routers with Prometheus
Get the router password for basic authentication to scrape information from the router healthz endpoint:
```
oc get dc router -n default -o jsonpath='{.spec.template.spec.containers[*].env[?(@.name=="STATS_PASSWORD")].value}{"\n"}'
```

Add router scrape configuration and add the output from the command above to `[ROUTER_PW]`:
```
[ec2-user@master0 ~]$ oc edit configmap prometheus
    scrape_configs:
...
    - job_name: 'openshift-routers'
      metrics_path: '/metrics'
      scheme: http
      basic_auth:
        username: admin
        password: [ROUTER_PW]
      static_configs:
      - targets: ['router.default.svc.cluster.local:1936']
...
    alerting:
      alertmanagers:
```

### Deploy node-exporter
Delete the project node-selector, grant prometheus-node-exporter serviceaccount hostaccess and deploy the node-exporter DaemonSet.
```
oc annotate namespace openshift-metrics openshift.io/node-selector="" --overwrite
oc adm policy add-scc-to-user -z prometheus-node-exporter -n openshift-metrics hostaccess
oc create -f resource/node-exporter.yaml -n openshift-metrics
``` 

Add scrape configuration for node-exporter:
```
[ec2-user@master0 ~]$ oc edit configmap prometheus -n openshift-metrics
    scrape_configs:
...
    - job_name: 'node-exporters'
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        insecure_skip_verify: true
      kubernetes_sd_configs:
      - role: node
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - source_labels: [__meta_kubernetes_role]
        action: replace
        target_label: kubernetes_role
      - source_labels: [__address__]
        regex: '(.*):10250'
        replacement: '${1}:9100'
        target_label: __address__
...
    alerting:
      alertmanagers:
```

Open port for Prometheus node-exporter:
```
[ec2-user@master0 ~]$ ansible nodes -m iptables -a "chain=OS_FIREWALL_ALLOW protocol=tcp destination_port=9100 jump=ACCEPT comment=node-exporter"
[ec2-user@master0 ~]$ ansible nodes -m shell -a "iptables-save | tee /etc/sysconfig/iptables"
```

### Deploy kube-state-metrics
Documentation: https://github.com/kubernetes/kube-state-metrics
``` 
oc create -f resource/kube-state-metrics.yaml -n openshift-metrics
```

Add kube-state-metric scrape configuration.
```
[ec2-user@master0 ~]$ oc edit configmap prometheus -n openshift-metrics
   scrape_configs:
...
    - job_name: 'kube-state-metrics'
      metrics_path: '/metrics'
      scheme: http
      static_configs:
      - targets: ['kube-state.openshift-metrics.svc.cluster.local:80']
...
    alerting:
      alertmanagers:
```

### Access Prometheus
This creates a new project called `openshift-metrics`. As soon as the pod is running you will be able to access it with the user `cheyenne`.
https://prometheus-openshift-metrics.app[X].lab.openshift.ch/

---

[← back to the labs overview](../README.md)

