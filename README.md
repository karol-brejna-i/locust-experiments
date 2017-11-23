Recently we were supposed to conduct a load/stress testing session. 

There were already some python scripts in place and the team that produced them suggested using locust.io for this purpose.

The tool was new to me. At the first glance, as far as feature list is concerned, Locust seems inferior to other software we used before, like Gatling or even JMeter (the latter is turning 20 soon, but it doesn't make it an invalid testing tool!). 
It looks like Locust generates load and that's pretty much it. With the exception of the single feature that 
I think is its strongest selling point: the ability to distribute the load (single master, multiple slaves) out of the box.

The authors also claim that it's very easy to use and to extend Locust. So, instead of discarding it (using Locust),
I decided to give it a quick try and try to address potential needs/problems with series of quick experiments.

Some of the things I would like to confirm are:
* Running on Kubernetes (but first [in the docker](docker-image/))
* Testing non-REST apps
* Dealing with long-running requests
* Capturing atomic results (now Locust saves pre-aggregated results)
* Enriching test result data (tags, etc.)
* Emitting the result to external data store

This repo holds results of particular experiments.

