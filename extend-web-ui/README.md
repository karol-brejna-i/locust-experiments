Locust provides a small HTTP API and a Web UI to control the execution of the tests and browsing through the results.
One can use the API, for example, to automatically trigger stress tests as a part of a build process.

What if we want to extend the UI by adding some customized result views, new actions?

According to [the docs](https://docs.locust.io/en/latest/extending-locust.html), it should be fairly easy.

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

One last thing to mention here is what needs to be done in order to access K8s API from the pod.
I chose to obtain an authentication token a do the HTTP request myself.
According to the official documentation, the preferred way is either using `kube-proxy`
or a programmatic client (see [this article](https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/#accessing-the-api-from-a-pod) for details).
For some real heavy lifting I would probably go for the client,
but decided to stay plain for the sake of simplicity.

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
(actually: crippled it greatly; I didn't want to focus on the UI part, but just prove the point so I did a minimal effort here)
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
This work depends on [previous experiment](https://medium.com/locust-io-experiments/locust-io-experiments-running-in-kubernetes-95447571a550) which point was to create Kubernetes descriptors for Locust. See [this folder](../kubernetes) for the scripts and info on how to use them

Basic K8s mechanics here are intact, the difference being [the config map that holds update Locust scripts](./kubernetes/scripts-cm.yaml).

In short, creating Locust cluster in K8s can be done these commands (if Kubernetes is up and running):

```bash
> git clone https://github.com/karol-brejna-i/locust-experiments.git
> cd locust-experiments
> cd kubernetes
> kubectl create -f locust-cm.yaml -f scripts-cm.yaml -f master-deployment.yaml -f service.yaml -f slave-deployment.yaml -f ingress.yaml
```

I am assuming you have done it already (while running the previous experiments) and locust nodes are running.

So, now let’s go to *extend-web-ui* folder (here are the sources for current excercise) and update the configmap:

```bash
> cd ../extend-web-ui
> kubectl replace -f kubernetes/scripts-cm.yaml
configmap "scripts-cm" replaced
> kubectl delete pods -l 'role in (locust-master, locust-slave)'
```

The last line (restart of pods) is here to make sure new configuration is used by Locust.

# In action

So, let’s open rescale form in the browser — <http://192.168.1.123/locust/rescale-form> (my K8s cluster’s IP is 192.168.1.123).

Remember when I claimed I trimmed down the original template. Well, actually: I crippled it greatly which you can see by yourself. I didn’t want to focus on the UI part, but just to prove the point — so I made a minimal effort here.

Still, this simple form let’s us submit a new number of workers. This cluster has two workers. Let’s go for 4 slaves now. After submitting, proper command is sent to Kubernetes and the user gets redirected to the main page.

In the upper right corner you will see that after a while the number of slaves has been increased.

We are doing so well, so we could try something braver: let’s do a downscale (to 1 worker) and then another upscale (to 3) straight away.

And here is a little surprise. Instead of **expected 3 workers **at the end, **I see 6 of them** on the UI.



Checking how many workers are really there:

```
$ kubectl get pods
NAME                            READY     STATUS    RESTARTS   AGE
locust-master-5d8fbbc6-46k6n    1/1       Running   0          5m
locust-slave-54c84df478-nh7wn   1/1       Running   0          31s
locust-slave-54c84df478-rt8fn   1/1       Running   0          31s
locust-slave-54c84df478-v65ng   1/1       Running   0          5m
```

There are three of them, as there should be.

Inspecting the master’s logs (`kubectl logs -l=’role=locust-master’ | grep “^\[“`) confirms, that communication with K8s was effective (Kubernetes did what we asked it to). The following lines seems to bring us closer to the diagnosis:

```
$ kubectl logs -l='role=locust-master' | grep -i client
[2018-01-27 09:44:24,028] locust-master-5d8fbbc6-46k6n/INFO/locust.runners: Client 'locust-slave-54c84df478-v65ng_27bb7f77ee2d982e6a0939cfde2618c1' reported as ready. Currently 1 clients ready to swarm.
[2018-01-27 09:44:24,494] locust-master-5d8fbbc6-46k6n/INFO/locust.runners: Client 'locust-slave-54c84df478-fhsld_451b6e5d6e1b851ad5ea5d20ebdd7787' reported as ready. Currently 2 clients ready to swarm.
[2018-01-27 09:45:45,733] locust-master-5d8fbbc6-46k6n/INFO/locust.runners: Client 'locust-slave-54c84df478-dj2qt_51c68108848c6a838c4b61cf850ec4b7' reported as ready. Currently 3 clients ready to swarm.
[2018-01-27 09:45:46,335] locust-master-5d8fbbc6-46k6n/INFO/locust.runners: Client 'locust-slave-54c84df478-njclx_996e9223e8e374ad526bae3abbbbaec2' reported as ready. Currently 4 clients ready to swarm.
[2018-01-27 09:49:12,435] locust-master-5d8fbbc6-46k6n/INFO/locust.runners: Client 'locust-slave-54c84df478-nh7wn_dd3a1c4e0c85a52479e4fdff3e3bcc7d' reported as ready. Currently 5 clients ready to swarm.
[2018-01-27 09:49:12,967] locust-master-5d8fbbc6-46k6n/INFO/locust.runners: Client 'locust-slave-54c84df478-rt8fn_35a69286475396966318935fb369303a' reported as ready. Currently 6 clients ready to swarm.
```
These are the only traces of worker-client communication. My reasoning is that Locust workers are able to report for duty, but they are unable to inform the master when they cannot server the load anymore. Nor is there any keep-alive or heartbeat mechanism in place. I’ll leave inspection of the sources for later (Locust’s internal mechanics is not the core concern of this article, scaling is just an exemplary new action).

