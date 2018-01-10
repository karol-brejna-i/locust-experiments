This work bases on previous experiment which point was to create Kubernets scripts for Locust.

Basic K8s mechanics here are intact, the difference being the config map that holds Locust scripts.

The config map was generated from a directory holding required python files with kubectl:

```
kubectl create configmap scripts-cm --from-file locust-scripts/
kubectl get cm -o yaml scripts-cm > scripts-cm.yaml
```