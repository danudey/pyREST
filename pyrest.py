import json
from urlparse import urlparse, parse_qs
import httplib
import urllib
import urllib2
from collections import defaultdict

class RestException(Exception):
    def __init__(self, message, parent=None):
        if parent:
            body = parent.read()
            self.code = parent.code
            self.msg = parent.msg
            try:
                self.body = json.loads(body)
            except ValueError:
                self.body = {}
            self.rawbody = body
            self.url = parent.url
            self.headers = parent.headers.dict

        if 'exception' in self.body.keys():
            self.servererror = self.body['exception']
        elif 'error' in self.body.keys():
            self.servererror = self.body['error']
        else:
            self.servererror = "Unknown error"

        self.message = "%s %s %s: %s" % (message, self.code, self.msg, self.servererror)

    def __str__(self):
        return self.message


class UsageException(Exception):
    pass

class RestResponse(object):
    """A response to a REST request"""
    def __init__(self, code, msg, body, url, headers):
        super(RestResponse, self).__init__()
        self.code = code
        self.msg = msg
        try:
            self.body = json.loads(body)
        except ValueError:
            self.body = {}
        self.rawbody = body
        self.url = url
        self.headers = headers

class RestAPI(object):
    """A simple module to interact with a REST web API"""
    def __init__(self, baseurl=None, user_agent=None):
        super(rest, self).__init__()
        self.baseurl = baseurl
        self.user_agent = user_agent
        self.supportedschemes = ['http','https']

    def _mappingtoquery(self,query):
        """accepts a dict, returns a query string"""
        q = lambda x: urllib.quote(str(x))
        res = []
        for key in query:
            if isinstance(query[key],list) or isinstance(query[key],set):
                res.extend(["%s=%s" % (q(key),q(value)) for value in query[key]])
            else:
                res.append("%s=%s" % (q(key), q(query[key])))

        return '&'.join(res)

    def _combinequeries(self,*args):
        """accepts as many dicts as you want to pass; returns a query
        string with the merged contents of the dicts; duplicate key/value pairs
        are only represented once"""
        endquery = defaultdict(set)
        for query in args:
            if query:
                for key in query.keys():
                    if isinstance(query[key],list) or isinstance(query[key],set):
                        endquery[key] = endquery[key].union(set(query[key]))
                    else:
                        endquery[key].add(query[key])
        return endquery

    def urirequest(self, uri, method='GET', query=None, headers=None, body=None, qs_append=True):
        """accepts a uri, appends it to self.baseurl, and calls urlrequest with the result"""
        if not self.baseurl:
            raise UsageException("No base URL is configured")
        url = "%s%s" % (self.baseurl, uri)
        return self.urlrequest(url, method, headers, body)

    def urlrequest(self, url, method='GET', query=None, headers=None, body=None, qs_append=True):
        """Makes a REST request to the URL provided"""
        urlparts = urlparse(url)
        if urlparts.scheme not in self.supportedschemes:
            raise UsageException("This class only supports the following URL schemes: %s" % ' '.join(self.supportedschemes))
        if query and not isinstance(query,dict):
            raise UsageException("The query parameter must be a dict (for now)")

        if qs_append:
            origquery = parse_qs(urlparts.query)
        else:
            origquery = None

        newquery = self._mappingtoquery(self._combinequeries(origquery,query))

        if newquery:
            url = "%s://%s%s?%s" % (urlparts.scheme,urlparts.netloc,urlparts.path,newquery)
        else:
            url = "%s://%s%s" % (urlparts.scheme,urlparts.netloc,urlparts.path)

        # We build the request into a dict here so we can
        # dump it later for debugging purposes.
        request = {}
        request['url'] = url
        if body:
            if isinstance(body,str):
                request['data'] = body
            else:
                request['data'] = json.dumps(body)
        if headers:
            request['headers'] = headers

        request = urllib2.Request(**request)

        try:
            response = urllib2.urlopen(request)
            body = response.read()
            rresponse = RestResponse(response.code, response.msg, body, response.url, response.headers.dict)
        except urllib2.HTTPError, e:
            response = e
            raise RestException("HTTP Error", e)

        return rresponse