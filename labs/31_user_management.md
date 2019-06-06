## Lab 3.1: Manage Users

### OpenShift Authorization

Before you begin with this lab, make sure you roughly understand the authorization concept of OpenShift.
[Authorization](https://docs.openshift.com/container-platform/3.6/architecture/additional_concepts/authorization.html)

### Add User to Project

First we create a user and give him the admin role in the openshift-infra project.
Login to the master and create the local user with ansible on all masters (replace ```[password]```):
```
[ec2-user@master0 ~]$ ansible masters -a "htpasswd -b /etc/origin/master/htpasswd cowboy [password]"
```

Add the admin role to the newly created user, but only for the project `openshift-infra`:
```
[ec2-user@master0 ~]$ oc adm policy add-role-to-user admin cowboy -n openshift-infra
```

Now login with the new user from your client and check if you see the `openshift-infra` project:
```
[localuser@localhost ~]$ oc login https://console.user[X].lab.openshift.ch
Username: cowboy
Password:
Login successful.

You have one project on this server: "openshift-infra"

Using project "openshift-infra".
```

### Add Cluster Role to User

In order to keep things clean, we delete the created rolebinding for the `openshift-infra` project again and give the user "cowboy" the global "cluster-admin" role.

Login as "sheriff":
```
[ec2-user@master0 ~]$ oc login -u sheriff
```

Add the cluster-admin role to the created user:
```
[ec2-user@master0 ~]$ oc adm policy remove-role-from-user admin cowboy -n openshift-infra
role "admin" removed: "cowboy"
[ec2-user@master0 ~]$ oc adm policy add-cluster-role-to-user cluster-admin cowboy
cluster role "cluster-admin" added: "cowboy"
```

Now you can try to login from your client with user "cowboy" and check if you see all projects:
```
[localuser@localhost ~]$ oc login https://console.user[X].lab.openshift.ch
Authentication required for https://console.user[X].lab.openshift.ch (openshift)
Username: cowboy
Password:
Login successful.

You have access to the following projects and can switch between them with 'oc project <projectname>':

    appuio-infra
    default
    kube-public
    kube-system
    logging
    management-infra
    openshift
  * openshift-infra

Using project "openshift-infra".
```


### Create Group and Add User

Instead of giving privileges to single users, we can also create a group and assign a role to that group.

Groups can be created manually or synchronized from an LDAP directory. So let's first create a local group manually and add the user "cowboy" to it:
```
[ec2-user@master0 ~]$ oc login -u sheriff

[ec2-user@master0 ~]$ oc adm groups new deputy-sheriffs cowboy
NAME         USERS
deputy-sheriffs   cowboy
```

Add the cluster-role to the group "deputy-sheriffs":
```
[ec2-user@master0 ~]$ oc adm policy add-cluster-role-to-group cluster-admin deputy-sheriffs
cluster role "cluster-admin" added: "deputy-sheriffs"
```

Verify that the group has been added to the cluster-admins:
```
[ec2-user@master0 ~]$ oc get clusterrolebindings | grep cluster-admin
cluster-admin                                                         /cluster-admin                                                         sheriff, cowboy                system:masters, deputy-sheriffs               
```


### Evaluate Authorizations

It's possible to evaluate authorizations. This can be done with the following pattern:
```
oc policy who-can VERB RESOURCE_NAME
```

Examples:
Who can delete the `openshift-infra` project:
```
oc policy who-can delete project -n openshift-infra
```

Who can create configmaps in the `default` project:
```
oc policy who-can create configmaps -n default
```

You can also get a description of all available clusterroles and clusterrolebinding with the following oc command:
```
[ec2-user@master0 ~]$ oc describe clusterrole.rbac
```

```
[ec2-user@master0 ~]$ oc describe clusterrolebinding.rbac
```
https://docs.openshift.com/container-platform/3.11/admin_guide/manage_rbac.html

### Cleanup

Delete the group, entity and user:
```
[ec2-user@master0 ~]$ oc get group
[ec2-user@master0 ~]$ oc delete group deputy-sheriffs

[ec2-user@master0 ~]$ oc get user
[ec2-user@master0 ~]$ oc delete user cowboy

[ec2-user@master0 ~]$ oc get identity
[ec2-user@master0 ~]$ oc delete identity htpasswd_auth:cowboy

[ec2-user@master0 ~]$ ansible masters -a "htpasswd -D /etc/origin/master/htpasswd cowboy"
```

---

**End of Lab 3.1**

<p width="100px" align="right"><a href="32_update_hosts.md">3.2 Update Hosts →</a></p>

[← back to the Chapter Overview](30_daily_business.md)
