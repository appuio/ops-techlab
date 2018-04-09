Lab 3.1: Warmup 
============

Lab 3.1.2: Learn how to access the lab environment 
-------------
We will write "user[X]" during the labs for user specific documentations. Everybody gets an ID an needs to use this ID, to use his environment.

For example for ID 1:
https://console.user[X].lab.openshift.ch
=>
https://console.user1.lab.openshift.ch


There are three main ways we will access our environment. These ports need to be open from our place outgoing to Amazon AWS.
1. API: Using the oc client or through a web browser. (443/HTTPS)
    1. The console API will be available through: console.user[X].lab.openshift.ch
1. Router: The deployed apps will be available through the routers. We will access them mainly through a web browser. (443/HTTPS and 80/HTTP)
1. Architecture: We will connect through ssh to the bastion host. This will be our main control instance. (22/SSH) 
    1. You can connect to the bastion host through: ssh -i ~/.ssh/puzzle-techlab.pem ec2-user@bastion.user[X].lab.openshift.ch
