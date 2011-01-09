pyREST
------

pyREST is a half-complete REST interface module. It doesn't provide any specific interface
to any specific service, or make any (many?) assumptions about what type of service you're
accessing, beyond these:

1. You're using JSON to send request bodies and receive responses
2. Probably some other things I'll add later

USAGE
-----

Basic usage:

	import pyrest
	
	rest = pyrest.rest()
	response = r.urlrequest("http://api.twitter.com/1/statuses/public_timeline.json")

`response` then contains a `restresponse` object with various properties you can inspect and access. If
the request fails, a `RestException` is raised with (nearly) identical properties, including the original
HTTPException.

The `rest` class also supports a default base URL, to avoid repeating common prefixes in client code. To
use this functionality, you can use the `urirequest` method of the `rest` class.

	import pyrest
	
	rest = pyrest.rest(baseurl="http://api.twitter.com/1/")
	response = r.urirequest("statuses/public_timeline.json")

For the `urirequest` and `urlrequest` methods, you can pass a few parameters of interest:

* body - The HTTP request body (sent via POST if set); if this is a string, it will be sent as-is; otherwise, it will be converted to JSON or an exception thrown if that fails.
* query - A dictionary of key/value pairs to add to the URL. If a query string already exists in the URL, the two query strings will be merged by default (see `qs_append`)
* qs_append - a boolean, representing whether to append (actually merge) existing query strings with the `query` parameter, or if the existing query string should be overwritten.
* method - which HTTP method to use; unsupported (POST will be used if the `body` parameter is passed; otherwise GET is used)

TODO: Lots more to document; `query` and `qs_append` parameters to `urirequest` and `urlrequest`; maybe
merge both into one function. Also, document the `restresponse` and `RestException` classes (pretty simple).