This time I'll try to leverage event-based nature of Locust to test the following:

* atomic (individual, as opposed to aggregated) result collecting
* result enrichment (adding custom metadata to the results)
* using custom (non-HTTP) client
* automatically adding test method name to the results

In short: dedicated client triggers (fires) request_success and request_failure events with custom metadata.

For wordy explanation of what's happening here, see: https://medium.com/p/183d2ae4a4c2


## Locust fix required
Here is what Locust docs say about introducing new event listeners:

```
Event listeners can be registered at the module level in a locust file. Here’s an example:


from locust import events

def my_success_handler(request_type, name, response_time, response_length, **kw):
    print "Successfully fetched: %s" % (name)

events.request_success += my_success_handler



It’s highly recommended that you add a wildcard keyword argument in your listeners (the **kw in the code above), to prevent your code from breaking if new arguments are added in a future version.
```

In this experiments we created a custom client that produces some additional arguments for request_success (and failure) events
and introduces dedicated handlers that are capable of consuming extra data,  thanks to the advice above (using **kwargs).

Unfortunately, the default event handlers that locust delivers don't respect their own advice.
It has now **kwargs in method definitions (https://github.com/locustio/locust/blob/5e1ccc578e0984692890df455b00a94e06559321/locust/stats.py#L557):

```python
def on_request_success(request_type, name, response_time, response_length):
    global_stats.log_request(request_type, name, response_time, response_length)
```

So, if you'd try to run the code on current version (Locust 0.8.1), you get error like this:


```
[2018-02-28 15:00:21,839] standalone/INFO/stdout:
[2018-02-28 15:00:22,331] standalone/INFO/stdout: Connection to broker:997 initialized.
[2018-02-28 15:00:22,331] standalone/INFO/stdout:
[2018-02-28 15:00:22,394] standalone/INFO/stdout: Making a virtual data push to /metrics/
[2018-02-28 15:00:22,394] standalone/INFO/stdout:
[2018-02-28 15:00:22,435] standalone/ERROR/stderr: Traceback (most recent call last):
  File "/usr/local/lib/python3.6/site-packages/locust/core.py", line 271, in run
    self.execute_next_task()
  File "/usr/local/lib/python3.6/site-packages/locust/core.py", line 297, in execute_next_task
    self.execute_task(task["callable"], *task["args"], **task["kwargs"])
  File "/usr/local/lib/python3.6/site-packages/locust/core.py", line 309, in execute_task
    task(self, *args, **kwargs)
  File "/locust/locustfile.py", line 28, in task1
    self.client.push("/metrics/")
  File "/locust/ghost_client.py", line 32, in func_wrapper
    response_time=total_time, response_length=0, tag=function_name)
  File "/usr/local/lib/python3.6/site-packages/locust/events.py", line 27, in fire
    handler(**kwargs)
TypeError: on_request_success() got an unexpected keyword argument 'tag'

```