This time I'll try to leverage event-based nature of Locust to test the following:

* atomic (individual, as opposed to aggregated) result collecting
* result enrichment (adding custom metadata to the results)
* using custom (non-HTTP) client
* automatically adding test method name to the results

For wordy explanation of what's happening here, see: https://medium.com/p/183d2ae4a4c2