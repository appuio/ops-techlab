# APPUiO OpenShift Troubleshooting Cheat Sheet

## `oc` troubleshooting commands

**Get status of current project and its resources:**
```
oc status -v
```

**Show events:**
```
oc get events
```

**Show a pod's logs:**
```
oc logs [-f] [-c CONTAINER]
```

**Show assembled information for a resource:**
```
oc describe RESOURCE NAME
```

**Show a resource's definition:**
```
oc get RESOURCE NAME -o yaml|json
```

**Start a debug pod:**
```
oc debug RESOURCE/NAME
```

**Collect diagnostics:**
```
oc adm diagnostics
```


## Service logs

**Show logs for a specific service:**
```
journalctl -u UNIT [-f]
```

**Important services**:
- `atomic-openshift-master[-api|-controllers]`
- `atomic-openshift-node`
- `etcd`
- `docker`
- `openvswitch`
- `dnsmasq`
- `NetworkManager`
- `iptables`

