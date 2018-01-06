Distributed load testing using cloud computing is an attractive option for a variety of test scenarios.
Cloud platforms provide a high degree of infrastructure elasticity, making it easy
to test applications and services with large numbers of simulated clients, each generating traffic patterned after users or devices.
Additionally, the pricing model of cloud computing fits very well with the very elastic nature of load testing.


Locust supports running load tests on multiple machines. It's a perfect fit for Kubernetes which makes distributed deployments,
container orchestration and scaling easy.

In this installment of my Locust experiments, I'll prepare Kubernetes (alias k8s) scripts for deploying and managing
Locust cluster and see if there are any surprises along the way.


> This piece is not about explaining K8s. There are already great sources of knowledge for the topic, including the product's homepage  - kubernetes.io. I'll focus on describing how to set up and how to use Locust in K8s.

# Locust distributed mode

Running Locust in distributed mode is described in its documentation.
In short:
* you can have one master and multiple slave nodes (workers)
* you need to tell the workers where the master is (give them the IP address and ports)
* you need to supply each worker with the tests code (locustfiles)
* the workers need to be able to connect to the master.

That's pretty much it.

# Kubernetes components
Let's dive in and go through the building blocks of the Locust cluster to be deployed.

Kubernetes' *configmaps* will help configure Locust. 
[One configmap](./scripts-cm.yaml) will hold a proper locustfile and will be mounted as a volume to the master and workers, 
[the second](./locust-cm.yaml) will contain other configuration settings (URL for tested host/service, for example) that will be injected to running Locust nodes as environment variables.


I'll use *deployment* in order to "ask" K8s for making sure our [master](./master-deployment.yaml) and [slaves](./slave-deployment.yaml) are up and running. 
[The service](./service.yaml) will make the master addressable within the cluster.

# Cluster deployment

All the source files used below are stored in /kubernetes directory of the experiments repo. Let's set up the cluster. 
(I assume that kubernetes is up and running and kubectl is able to connect to the cluster.)

    > git clone https://github.com/karol-brejna-i/locust-experiments.git
    > cd locust-experiments
    > cd kubernetes
    > kubectl create -f locust-cm.yaml -f scripts-cm.yaml -f master-deployment.yaml -f service.yaml -f slave-deployment.yaml

*kubectl* command connects to my minikube cluster and crate the components mentioned above. 
If ran for the first time, it may take a while to complete (if there is no locust docker image on the cluster, it needs to be downloaded first).
To see, if locust nodes are running we can inspect if the pods are up:

    > kubectl get -w pods
    NAME                             READY     STATUS    RESTARTS   AGE
    locust-master-754dc88dd8-zgs7m   1/1       Running   0          24m
    locust-slave-7c89bfc5b7-4cms8    1/1       Running   0          24m
    locust-slave-7c89bfc5b7-f7p4l    1/1       Running   0          24m

From the output we can pick up the master name can also take a look at the logs.
`kubectl logs locust-master-754dc88dd8-zgs7m` should include the following information:

```
[2018-01-02 08:05:14,662] locust-master-754dc88dd8-zgs7m/INFO/locust.main: Starting web monitor at *:8089
[2018-01-02 08:05:14,666] locust-master-754dc88dd8-zgs7m/INFO/locust.main: Starting Locust 0.8.1
[2018-01-02 08:05:15,741] locust-master-754dc88dd8-zgs7m/INFO/locust.runners: Client 'locust-slave-2800781981-wrbl4_ed388a7a4bd15b51d094ae3afb05dc35' reported as ready. Currently 1 clients ready to swarm.
[2018-01-02 08:05:16,779] locust-master-754dc88dd8-zgs7m/INFO/locust.runners: Client 'locust-slave-2800781981-cz2n8_74c58b7509b00b5be5d4ab05c4f87abf' reported as ready. Currently 2 clients ready to swarm.
```

We can see that the master has started (line 1 and 2) and the slaves "volunteer" to do some work (lines 3-4).

# First test run
Nothing more is happening there, because we still need to tell the master to start the tests. Normally, you'd probably use neat Locust UI for this. You can also take advantage of HTTP API, which is particularly useful for test automation etc. (for example, when you want to start a stress test as a part of your CI/CD pipeline).
I'll use two master's endpoints here: `/swarm` to start the tests and `/stop` to finish them.
We have a K8s service defined for the master, so the URLs gonna be:
* http://locust-master:8089/swarm
* http://locust-master:8089/stop

Quick note: Kubernetes job is to make sure that containers in the cluster can communicate with each other.
Please, mind that by default the containers are not accessible externally. So, in order to make the calls, we'll create a short live container which sole role will be to issue a single curl command.

In the deployment scripts we configured locust master to periodically dump activity logs to the console (with print-stats switch) so we can listen to the logs in one terminal (to check the results):

    kubectl logs -f locust-master-754dc88dd8-zgs7m

and start the test in the second one:

    >  kubectl run strzal --image=djbingham/curl --restart='OnFailure' -i --tty --rm --command -- curl -X POST -F 'locust_count=4' -F 'hatch_rate=4' http://locust-master:8089/swarm
    {"success": true, "message": "Swarming started"}

After some time, stop the test:

    >  kubectl run strzal --image=djbingham/curl --restart='OnFailure' -i --tty --rm --command -- curl http://locust-master:8089/stop
    {"success": true, "message": "Test stopped"}

For me, all went well, which the following log proves:

```
 Name                                                          # reqs      # fails     Avg     Min     Max  |  Median   req/s
--------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------
 Total                                                              0     0(0.00%)                                       0.00

[2018-01-02 08:10:08,440] locust-master-754dc88dd8-zgs7m/INFO/locust.runners: Sending hatch jobs to 2 ready clients
 Name                                                          # reqs      # fails     Avg     Min     Max  |  Median   req/s
--------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------
 Total                                                              0     0(0.00%)                                       0.00

 Name                                                          # reqs      # fails     Avg     Min     Max  |  Median   req/s
--------------------------------------------------------------------------------------------------------------------------------------------
 GET /stats/requests                                                3     0(0.00%)       9       5      14  |       9    0.00
--------------------------------------------------------------------------------------------------------------------------------------------
 Total                                                              3     0(0.00%)                                       0.00

 Name                                                          # reqs      # fails     Avg     Min     Max  |  Median   req/s
--------------------------------------------------------------------------------------------------------------------------------------------
 GET /                                                              3     0(0.00%)      12       4      28  |       5    0.00
 GET /stats/requests                                                5     0(0.00%)       8       5      14  |       9    0.00
--------------------------------------------------------------------------------------------------------------------------------------------
 Total                                                              8     0(0.00%)                                       0.00

 Name                                                          # reqs      # fails     Avg     Min     Max  |  Median   req/s
--------------------------------------------------------------------------------------------------------------------------------------------
 GET /                                                              5     0(0.00%)       9       4      28  |       4    1.33
 GET /stats/requests                                               15     0(0.00%)       5       4      14  |       4    2.67
--------------------------------------------------------------------------------------------------------------------------------------------
 Total                                                             20     0(0.00%)                                       4.00

 Name                                                          # reqs      # fails     Avg     Min     Max  |  Median   req/s
--------------------------------------------------------------------------------------------------------------------------------------------
 GET /                                                              9     0(0.00%)       7       4      28  |       4    1.20
 GET /stats/requests                                               17     0(0.00%)       5       4      14  |       4    2.80
--------------------------------------------------------------------------------------------------------------------------------------------
 Total                                                             26     0(0.00%)                                       4.00
```

What you can see here is:
* some inactivity period, stats from before the test was started (lines 1-4)
* the moment that the master delegated the work to the slaves (line 6)
* growing number of request (starting from line 7)

# External access

As mentioned before, typically, services and pods have addresses only routable by the cluster network.
You need to put some effort in order to expose them to the outside world.
Let's examine, how making Locust web console accessible from the internet would work.

The final piece of the  puzzle here is an ingress which is K8s' mechanism that allows inbound connections to reach the cluster services.

> Note: If you are using minikube (as I am), mind that ingress controller is delivered as an add-on, that is not enabled by default. You need to do it yourself. For me, the following command did the trick: `minikube addons enable ingress`

According to this simple rule:

```
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    ingress.kubernetes.io/rewrite-target: /
    ingress.kubernetes.io/ssl-redirect: "false"
  name: locust
spec:
  rules:
  - http:
      paths:
      - backend:
          serviceName: locust-master
          servicePort: 8089
        path: /locust
```

`locust-master` service is exposed so the users can reach Locust web UI under `/locust` URL on the host.

Let's create the ingress with `kubectl create -f ingress.yaml` (check the file location in "Cluster deployment" section),
get the cluster IP with minikube ip (192.168.1.123 in my case) and put expected locust URL in the browser (explorer http://192.168.1.123/locust/).
Unfortunately, although Locust web page is accessible, it's all mangled and nonfunctional.

It turns out that the URLs for page resources (CSS, js) and the HTTP API are absolute (actually: root-relative).
By using the ingress we "moved" the page address from the root (`/`) to `/locust` and the page got confused. Programmed this way, Locust cannot be properly accessed via ingress (or put behind a reverse proxy, load balancer for that matter).

# External access - the fix
Well, Locust.io is an open source project, for good and for bad. Let's make use of it.
After inspecting the sources, it turns out that the fix (that would allow serving Locust UI under URL different than /) is pretty simple. Take a look at this pull request: https://github.com/locustio/locust/pull/692/files
When the PR is merged or you build Locust docker image with these changes (see: /docker-url-fix folder in the sources GitHub repository), the UI starts working just fine.