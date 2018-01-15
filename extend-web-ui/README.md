Locust provides a small HTTP API and a Web UI to control the execution of the tests and browsing through the results. 
One can use the API, for example, to automatically trigger stress tests as a part of build process.

What if we want to extend the UI by adding some customized result views, new actions?

According to [the docs](https://docs.locust.io/en/latest/extending-locust.html) it should be fairly easy.

# The goal

Now, that we are able to run Locust in Kubernetes (see: [/kubernetes](../kubernetes)) it (K8s) will allow us easily rescale the cluster.

This simple command will do:
```
> kubectl scale --replicas=3 deployment/locust-slave
```

Let's be nice to the users and not force them to use command line tools (use a terminal connected to K8s cluster) and **prepare some graphical user interface to perform this action**.

# Components of the solution

What we'll need (the minimal version) is:
* a code that will hold the logic (communicate with K8s and perform rescale)
* HTTP endpoint that exposes the functionality 
* a web form that where new number of slaves can be entered
 
## The logic
In our code, we want to repeat the same thing that `kubectl scale` command is doing.  
Let's sniff the traffic that kucectl generates so we can see what APIs are used there:
```
kubectl scale --v=6 --replicas=1 deployment/locust-master

[...]
I0111 03:54:04.683167   10293 round_trippers.go:395] GET https://kube-apiserver-dxb1.istdx.infra-host.com/apis/extensions/v1beta1/namespaces/default/deployments/locust-master
I0111 03:54:04.942727   10293 round_trippers.go:395] PUT https://kube-apiserver-dxb1.istdx.infra-host.com/apis/extensions/v1beta1/namespaces/default/deployments/locust-master
[...]
```

It looks like it GETs current deploment definition, updates `replicas` count and PUTs modified deployment back.
(Ok, I cheated. Actually, I used `--v=8` switch which shows not only HTTP operations, but also request/response bodies. The presenting this output would overflow the boundaries of this article...)  

Digging a bit deeper, it turns out that we can be even smarter and do the change in a single PATCH request. Take a look at this pseudo-code:
```
    data = f'[{{"op":"replace","path":"/spec/replicas","value": {replicas_count}}}]'
    endpoint = f"{KUBERNETES_URL}/apis/extensions/v1beta1/namespaces/{namespace}/deployments/{deployment}/scale"
    
    result = requests.patch(endpoint, headers=self.headers, data=data, verify=False)
``` 

The code performing required action is collected in [kubernetes.py](./locust-scripts/kubernetes.py).


## Web form

## Web endpoint

