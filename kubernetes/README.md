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
    
...    