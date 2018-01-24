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
* code that will hold the logic (communicate with K8s and perform rescale)
* HTTP endpoint that exposes the functionality 
* a web form that where new number of slaves can be entered
 
## The logic
In our code, we want to repeat the same thing that `kubectl scale` command is doing.  
Let's sniff the traffic that kubectl generates so we can see what APIs are used there:
```
kubectl scale --v=6 --replicas=1 deployment/locust-master

[...]
I0111 03:54:04.683167   10293 round_trippers.go:395] GET https://kube-apiserver-dxb1.istdx.infra-host.com/apis/extensions/v1beta1/namespaces/default/deployments/locust-master
I0111 03:54:04.942727   10293 round_trippers.go:395] PUT https://kube-apiserver-dxb1.istdx.infra-host.com/apis/extensions/v1beta1/namespaces/default/deployments/locust-master
[...]
```

It looks like it GETs current deployment definition, updates `replicas` count and PUTs modified deployment back.
(Ok, I cheated. Actually, I used `--v=8` switch which shows not only HTTP operations, but also request/response bodies. The presenting this output would overflow the boundaries of this article...)

Digging a bit deeper, it turns out that we can be even smarter and do the change in a single PATCH request. Take a look at this pseudo-code:
```
    data = f'[{{"op":"replace","path":"/spec/replicas","value": {replicas_count}}}]'
    endpoint = f"{KUBERNETES_URL}/apis/extensions/v1beta1/namespaces/{namespace}/deployments/{deployment}/scale"
    
    result = requests.patch(endpoint, headers=self.headers, data=data, verify=False)
``` 

The code performing required action is collected in [kubernetes.py](./locust-scripts/kubernetes.py).

## Web endpoint
Locust makes use of Flask to deliver it's web user interface (see: https://github.com/locustio/locust/blob/master/locust/web.py).

Adding your own endpoint is just a matter of proper `route` annotation.
In this example, I created two endpoints - one responsible for displaying rescale form and one for performing the action.
See the following pseudo-code:

```python
from locust import web

@web.app.route("/rescale-form")
def cluster_rescale_form():
    return generate_form()


@web.app.route("/rescale", methods=['POST'])
def rescale_action():
    [...]
    return redirect("/", 302)
```

The actual code resides in the enclosed [locustfile](./locust-scripts/locustfile.py).

## Web form
Being a flask app, the UI can utilize [Jinja2](http://jinja.pocoo.org/) to generate the pages.
For this experiment I trimmed down [the template used by Locust itself](https://github.com/locustio/locust/blob/master/locust/templates/index.html)
so my web form looks at least a bit similar to the rest of the UI.

Key part of [rescale-form.html](./locust-scripts/rescale-form.html) is the following form:
```html
<form action="./rescale" method="POST" id="rescale_form">
    <label for="worker_count">Number of workers in the cluster</label>
    <input type="text" name="worker_count" id="worker_count" class="val" /><br>
    <button type="submit">Rescale</button>
</form>
```

And these are all the required parts.

# Deployment
This work depends on [previous experiment](https://medium.com/locust-io-experiments/locust-io-experiments-running-in-kubernetes-95447571a550) which point was to create Kubernetes descriptors for Locust. See the [this folder](../kubernetes) for the scripts and info on how to use them

Basic K8s mechanics here are intact, the difference being [the config map that holds update Locust scripts](./kubernetes/scripts-cm.yaml).

In short, creating Locust cluster in K8s can be done these commands (assuming Kubernetes is up and running):

    > git clone https://github.com/karol-brejna-i/locust-experiments.git
    > cd locust-experiments
    > cd kubernetes
    > kubectl create -f locust-cm.yaml -f scripts-cm.yaml -f master-deployment.yaml -f service.yaml -f slave-deployment.yaml -f ingress.yaml


# In action

