# Feeding the locusts
There are times when you want your Locust scripts to use some specific input data in order to perform the tests.

For example: 
* you want to use a list of users and their credentials in order to log in to some service,
* you have a set of form values that need to be submitted,
* you need to upload specific files as a part of requests to your service,
* you want to have repeatable/comparable test conditions (by providing the exact same input data),
* you have some data that exploits the service's corner cases (validation, special values, special characters, etc.).

In this "episode", I'll try to examine one of the ways of addressing such problems. 

Along the way, the following "techniques" will be used here, which can also be useful in other Locust tests developments:
* determining if the code runs on master or slave,
* doing some preparations before the tests start,
* sending some data from the master to workers.

See the following article for more detailed walk through: https://medium.com/locust-io-experiments/locust-experiments-feeding-the-locusts-cf09e0f65897


## Scope of the experiment
This experiment is trying to deliver the following requirements:

Assume, that we are testing a web service's endpoint that accepts **POST requests with JSON payload**.
For this, we want to use a **specific data set**. Let's say, we have a **CSV file** where every row represents a single message to be sent. We want to be able to read the content **before the tests start**.
Furthermore, we require being able to run the test in a **distributed manner ** -  running multiple slave workers that will issue the POST request.
Moreover, we don't want to have **any duplicates** (sending the same value more than once).

## Contents of this repository

* [0mq-playground](./0mq-playground) - some experiments that helped me understand some 0MQ mechanics
* [data](./data) - example data explanation plus description on how to use some other dataset
* [locust-scripts](./locust-scripts) - the folder for locust files
* [docker-compose.yml](./docker-compose.yml) and [docker-compose-headless.yml](./docker-compose-headless.yml) - for setting up development cluster

## Development environment setup
For testing the solution we need to run Locust in distributed mode. 
You could do this by manually running master and slaves yourself from the command line. 
Another option here is doing it with kubernetes (https://medium.com/locust-io-experiments/locust-io-experiments-running-in-kubernetes-95447571a550)

This time, on the other hand, I'll use Docker Compose (my Kubernetes doesn't want to get up after last Windows update...).

For setting up the cluster two versions of docker compose configuration were created:
one for running Locust headless (without web UI) and one for running the UI, too.


Docker compose files include the definition of services for **Locust master and locust slave** with all required environment
variables set and a volume containing test code configured. They also contain a small section for **simulating the system under test** was included.

The whole use case (to remind you) is about reading some input data and using them to form POST requests.
In order not to write anything here, I quickly googled out docker image that will play the role of the tested system.

The service is able to accept different requests, including POST, and it will simply log the request
(with the body) so we can confirm which data was used.

Maybe mocking the system under test could be easier. 
For me, using "kennethreitz/httpbin" and "lucascimon/nginx-logging-proxy" docker images was the quickest.

## Running the experiment
To set up a cluster and start the tests the following command can be run within the terminal:
```bash
docker-compose -f docker-compose-headless.yml up
```

This will bring up all the containers - Locust master, slave, tested service - and start logging in the console.
The logs will represent the order of events: starting the nodes, reading the input data by the master, starting the "feeder" and then requesting new data by the slave and using them to issue POST request:

```
$ docker-compose -f docker-compose-headless.yml up
Creating network "feeding-locusts_default" with the default driver
Creating master                  ... done
Creating httpbin                 ... done
Creating sut                     ... done
Creating feeding-locusts_slave_1 ... done
Attaching to httpbin, sut, master, feeding-locusts_slave_1
httpbin    | [2019-04-07 08:29:24 +0000] [1] [INFO] Starting gunicorn 19.9.0
httpbin    | [2019-04-07 08:29:24 +0000] [1] [INFO] Listening at: http://0.0.0.0:80 (1)
httpbin    | [2019-04-07 08:29:24 +0000] [1] [INFO] Using worker: gevent
httpbin    | [2019-04-07 08:29:24 +0000] [8] [INFO] Booting worker with pid: 8
sut        | + DEFAULT_LOG_FORMAT='$remote_addr [$time_local] $request $status req_time=$request_time body=$request_body'
sut        | + : http://httpbin:80
sut        | + : 80
sut        | + LOG_FORMAT='$remote_addr [$time_local] $request $status req_time=$request_time body=$request_body'
sut        | + cat
sut        | + cat
sut        | + exec nginx -g 'daemon off;'
sut        | 2019/04/07 08:29:24 [notice] 1#1: using the "epoll" event method
sut        | 2019/04/07 08:29:24 [notice] 1#1: nginx/1.13.9
sut        | 2019/04/07 08:29:24 [notice] 1#1: built by gcc 6.3.0 20170516 (Debian 6.3.0-18)
sut        | 2019/04/07 08:29:24 [notice] 1#1: OS: Linux 4.9.125-linuxkit
sut        | 2019/04/07 08:29:24 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
sut        | 2019/04/07 08:29:24 [notice] 1#1: start worker processes
sut        | 2019/04/07 08:29:24 [notice] 1#1: start worker process 8
master     | [2019-04-07 08:29:25,308] master/INFO/stdout: Reading input data...
master     | [2019-04-07 08:29:25,308] master/INFO/stdout:
master     | [2019-04-07 08:29:25,319] master/INFO/stdout: 1000 records read
master     | [2019-04-07 08:29:25,319] master/INFO/stdout:
master     | [2019-04-07 08:29:25,321] master/INFO/root: Waiting for slaves to be ready, 0 of 1 connected
slave_1    | [2019-04-07 08:29:25,474] cbbab4894226/INFO/locust.main: Starting Locust 0.9.0
master     | [2019-04-07 08:29:25,477] master/INFO/locust.runners: Client 'cbbab4894226_d66ee410ec561a91df67e14da8ff4391' reported as ready. Currently 1 clients ready to swarm.
master     | [2019-04-07 08:29:26,322] master/INFO/locust.runners: Sending hatch jobs to 1 ready clients
master     | [2019-04-07 08:29:26,322] master/INFO/stdout: on_master_start_hatching
master     | [2019-04-07 08:29:26,322] master/INFO/stdout:
master     | [2019-04-07 08:29:26,322] master/INFO/locust.main: Run time limit set to 10 seconds
master     | [2019-04-07 08:29:26,322] master/INFO/locust.main: Starting Locust 0.9.0
slave_1    | [2019-04-07 08:29:26,323] cbbab4894226/INFO/locust.runners: Hatching and swarming 1 clients at the rate 1 clients/s...
slave_1    | [2019-04-07 08:29:26,324] cbbab4894226/INFO/stdout: zmq consumer initialized
slave_1    | [2019-04-07 08:29:26,324] cbbab4894226/INFO/stdout:
slave_1    | [2019-04-07 08:29:26,324] cbbab4894226/INFO/stdout: task1
slave_1    | [2019-04-07 08:29:26,324] cbbab4894226/INFO/stdout:
slave_1    | [2019-04-07 08:29:26,325] cbbab4894226/INFO/stdout: announcing I am available
slave_1    | [2019-04-07 08:29:26,325] cbbab4894226/INFO/stdout:
master     | [2019-04-07 08:29:26,329] master/INFO/stdout: zmq feeder initialized
master     | [2019-04-07 08:29:26,329] master/INFO/stdout:
master     | [2019-04-07 08:29:26,329] master/INFO/stdout: start sending...
master     | [2019-04-07 08:29:26,329] master/INFO/stdout:
master     | [2019-04-07 08:29:26,329] master/INFO/stdout: before receive
master     | [2019-04-07 08:29:26,329] master/INFO/stdout:
master     | [2019-04-07 08:29:26,470] master/INFO/stdout: after receive
master     | [2019-04-07 08:29:26,329] master/INFO/stdout:
slave_1    | [2019-04-07 08:29:26,470] cbbab4894226/INFO/stdout: using the following data to make a request {'Number': '1', 'Id': '1503014', 'Name': 'Carlsen, Magnus', 'Title': 'GM', 'Fed': 'Norway', 'Elo': '2845', 'NElo': '', 'Born': '1990', 'flag': '', 'Games': '', 'Club/City': 'OSG Baden-Baden', '#Trns': '230'}
slave_1    | [2019-04-07 08:29:26,482] cbbab4894226/INFO/stdout: task1
slave_1    | [2019-04-07 08:29:26,482] cbbab4894226/INFO/stdout:
slave_1    | [2019-04-07 08:29:26,482] cbbab4894226/INFO/stdout: announcing I am available
slave_1    | [2019-04-07 08:29:26,482] cbbab4894226/INFO/stdout:
master     | [2019-04-07 08:29:26,483] master/INFO/stdout: after receive
master     | [2019-04-07 08:29:26,483] master/INFO/stdout:
slave_1    | [2019-04-07 08:29:26,484] cbbab4894226/INFO/stdout: using the following data to make a request {'Number': '2', 'Id': '2020009', 'Name': 'Caruana, Fabiano', 'Title': 'GM', 'Fed': 'USA', 'Elo': '2828', 'NElo': '', 'Born': '1992', 'flag': '', 'Games': '', 'Club/City': '', '#Trns': '987'}
slave_1    | [2019-04-07 08:29:26,484] cbbab4894226/INFO/stdout:
master     | [2019-04-07 08:29:26,484] master/INFO/stdout: before receive
master     | [2019-04-07 08:29:26,484] master/INFO/stdout:
sut        | 172.22.0.5 [07/Apr/2019:08:29:26 +0000] POST /post HTTP/1.1 200 req_time=0.004 body={\x22Number\x22: \x221\x22, \x22Id\x22: \x221503014\x22, \x22Name\x22: \x22Carlsen, Magnus\x22, \x22Title\x22: \x22GM\x22, \x22Fed\x22: \x22Norway\x22, \x22Elo\x22: \x222845\x22, \x22NElo\x22: \x22\x22, \x22Born\x22: \x221990\x22, \x22flag\x22: \x22\x22, \x22Games\x22: \x22\x22, \x22Club/City\x22: \x22OSG Baden-Baden\x22, \x22#Trns\x22: \x22230\x22}
sut        | 172.22.0.5 [07/Apr/2019:08:29:26 +0000] POST /post HTTP/1.1 200 req_time=0.001 body={\x22Number\x22: \x222\x22, \x22Id\x22: \x222020009\x22, \x22Name\x22: \x22Caruana, Fabiano\x22, \x22Title\x22: \x22GM\x22, \x22Fed\x22: \x22USA\x22, \x22Elo\x22: \x222828\x22, \x22NElo\x22: \x22\x22, \x22Born\x22: \x221992\x22, \x22flag\x22: \x22\x22, \x22Games\x22: \x22\x22, \x22Club/City\x22: \x22\x22, \x22#Trns\x22: \x22987\x22}
```

To destroy the cluster:
```bash
docker-compose -f docker-compose-headless.yml up
```

In the code I had also added appending the data received by slaves (with timestamps) to a text file called received.txt.
This way it is easier to track the data distribution.

After the test, you can inspect the file to check how fast and in which order was the data used. 




