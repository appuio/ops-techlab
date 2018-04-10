Lab 3.3: Daily business
============

Lab 3.3.1: User management 
-------------
## Add user to project
First we create a user and give him the admin role in the openshift-infra project.
Login to the master and create the local user
```
[ec2-user@master0 ~]$ sudo htpasswd -c /etc/origin/master/htpasswd test-user
```

Add the admin role of the project openshift-infra to the created user.
```
[ec2-user@master0 ~]$ oc adm policy add-role-to-user admin test-user -n openshift-infra
```

Now login with the new user and check if you see the openshift-infra project
```
[ec2-user@master0 ~]$ oc login https://console.[user].lab.openshift.ch:8443
Username: test-user
Password: 
Login successful.

You have one project on this server: "openshift-infra"

Using project "openshift-infra".
```

## Add user to cluster role
If the user is a cluster admin we should delete the created rolebinding for the project and give him the global clusterPolicyBinding "cluster-admin" role.

Login as system:admin
```
[ec2-user@master0 ~]$ oc login -u system:admin
```

Add the cluster-admin role to the created user.
```
[ec2-user@master0 ~]$ oc adm policy remove-role-from-user admin test-user -n openshift-infra
role "admin" removed: "test-user"
[ec2-user@master0 ~]$ oc adm policy add-cluster-role-to-user cluster-admin test-user
cluster role "cluster-admin" added: "test-user"
```
Now you can try to login with the user and check if you see all projects
```
[ec2-user@master0 ~]$ oc login https://console.[user].lab.openshift.ch:8443
Authentication required for https://console.user6.lab.openshift.ch:8443 (openshift)
Username: test-user
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

## Create a group and add user to the group
It is also possible to add a group with users to a cluster policy.
Create a local group and add test-user to it. (It's also possible to work with ldap/AD groups)
```
[ec2-user@master0 ~]$ oc adm groups new test-group test-user
NAME         USERS
test-group   test-user
```

Add the group to the cluster-role
```
[ec2-user@master0 ~]$ oc adm policy add-cluster-role-to-group cluster-admin test-group
cluster role "cluster-admin" added: "test-group"
```

Verifiy that the group is added to the cluster-admins
```
[ec2-user@master0 ~]$ oc get clusterrolebindings | grep cluster-admin
cluster-admin                                                         /cluster-admin                                                         shushu, test-user                system:masters, test-group               
```

## Evaluate authorizations
It's possible to evaluate authorizations. This can be done with the following pattern.
```
oc who-can VERB RESOURCE_NAME
```

Examples
Who can delete the openshift-infra project.
```
oc policy who-can delete project -n openshift-infra
```

Who can create configmaps in the default project.
```
oc policy who-can create configmaps -n default
```

## Delete resource
Delete the user and the group:
```
[ec2-user@master0 ~]$ oc delete group test-group
[ec2-user@master0 ~]$ oc get identity
[ec2-user@master0 ~]$ oc delete identity htpasswd_auth:test-user
[ec2-user@master0 ~]$ sudo htpasswd -D /etc/origin/master/htpasswd test-user
```

You can get all available clusterPolicies and clusterPoliciesBinding with the following oc command.
```
[ec2-user@master0 ~]$ oc login -u system:admin

[ec2-user@master0 ~]$ oc describe clusterPolicy default
[ec2-user@master0 ~]$ oc describe clusterPolicyBindings :default
```
