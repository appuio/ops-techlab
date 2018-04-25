## Lab 1.2: How to Access the Lab Environment

In the following labs, we are going to use `user[X]` as a placeholder for the user id that was assigned to you.

If you e.g. had user id 1 you would change
```
https://console.user[X].lab.openshift.ch
```
to
```
https://console.user1.lab.openshift.ch
```


There are three main ways we will access our environment. The mentioned ports need to be open from our own location to Amazon AWS.

- **API** / **Console**
  - Address: https://console.user[X].lab.openshift.ch
  - Port: 443/tcp

- **Applications**
  - Address: https://console.user[X].lab.openshift.ch
  - Ports: 80/tcp and 443/tcp

- **Administration**
  - Address: bastion.user[X].lab.openshift.ch
  - User: ec2-user
  - Command: `ssh ec2-user@bastion.user[X].lab.openshift.ch`
  - Port: 22/tcp

---

**End of Lab 1.2**

<p width="100px" align="right"><a href="20_installation.md">2. OpenShift Installation →</a></p>

[← back to the Chapter Overview](10_warmup.md)
