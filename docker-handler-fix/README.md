Dockerfile that prepares a patched version of Locust docker image (grubykarol/locust)

What it does is:
* pull Locust.io from GitHub
* go to last know good commit (as was known when implemented the fix)
* apply desired fix
* clean up

Usage identical to https://hub.docker.com/r/grubykarol/locust/.

The patch changes default request success/failure handlers by extending their declaration with `**kwargs`
so they can deal with custom metadata that users want to associate with the requests.

See https://medium.com/p/183d2ae4a4c2 for details.

## Build the image
```
docker build -t grubykarol/locust:0.8.1-py3.6-patch -t grubykarol/locust:latest .
```
