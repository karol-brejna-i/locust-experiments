cd kubernetes
kubectl create -f locust-cm.yaml -f scripts-cm.yaml -f master-deployment.yaml -f service.yaml -f slave-deployment.yaml
cd -


kubectl delete -f locust-cm.yaml -f scripts-cm.yaml -f master-deployment.yaml -f service.yaml -f slave-deployment.yaml



This work depends on previous experiment which point was to create Kubernetes scripts for Locust.

Basic K8s mechanics here are intact, the difference being the config map that holds Locust scripts.

The config map was generated from a directory holding required python files with kubectl:

```
kubectl delete cm scripts-cm
kubectl create configmap scripts-cm --from-file locust-scripts/
kubectl get cm -o yaml scripts-cm | sed '/creationTimestamp\|resourceVersion\|selfLink\|uid:/d' > kubernetes/scripts-cm.yaml
```





```bash
> cd ../extend-web-ui
> kubectl replace -f kubernetes/scripts-cm.yaml
configmap "scripts-cm" replaced
> kubectl replace -f kubernetes/locust-cm.yaml

> kubectl delete pods -l 'role in (locust-master, locust-slave)'
```