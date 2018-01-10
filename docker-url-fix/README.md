Dockerfile that prepares a patched version of Locust docker image (grubykarol/locust)

What it does is:
* pull Locust.io from GitHub
* go to last know good commit (as was known when implemented the fix)
* apply desired fix
* clean up

Usage identical to https://hub.docker.com/r/grubykarol/locust/.

The patch changes root-relative URLs in the web app (HTTP API, web page)
so it can be served behind a reverse proxy or Kubernetes ingress.