
    Recently a new version of Locust was released so I decided to use this as an excuse to refresh the docker image and show information on how to use it.
    The patch mentioned here was incorporated into Locust source codebase making this one obsolete.
        
    In additioon, I decided to create a dedicated repository for the docker image for Locust. If you visit https://github.com/karol-brejna-i/docker-locust, you’ll notice that the repo is organized so it can maintain many versions of the image.

### Please, visit https://github.com/karol-brejna-i/docker-locust for the latest version of the docker image.


# Original content:
Dockerfile that prepares a patched version of Locust docker image (grubykarol/locust)

What it does is:
* pull Locust.io from GitHub
* go to last know good commit (as was known when implemented the fix)
* apply desired fix
* clean up

Usage identical to https://hub.docker.com/r/grubykarol/locust/.

The patch changes root-relative URLs in the web app (HTTP API, web page)
so it can be served behind a reverse proxy or Kubernetes ingress.