"""Usage

class Items(ResourceManager):
    __resourcename__ = 'items'

    def get(self, item_id):
        return self.client.get('/items', item_id)


class MyAPI(BaseAPI):

    def __init__(self, base_url):
        super(MyAPI, self).__init__()
        self.client = JSONRequests(base_url)

    def for_resource(self, resource):
        ResourceManagerCls = self.resource_factory(resource)
        return ResourceManagerCls(self.client)


client = MyAPI('http://127.0.0.1:5000/api/v1')
items = client.for('items')
items.get(1)

"""

import json
import re

import requests


class ResourceManager(object):

    def __init__(self, client):
        self.client = client


class BaseAPI(object):

    def __init__(self):
        self.resources = {getattr(sc, '__resourcename__', cc_to_uc(sc.__name__)): sc
                          for sc in ResourceManager.__subclasses__()}

    def resource_factory(self, resource):
        """Factory function to get a resource manager instance

        :param resource: name of the resource
        :returns: resource manager class object
        :rtype: subclass of ResourceManager

        """
        return self.resources[resource]

    def for_resource(self, resource):
        """Get the resource manager instance for the resource

        :param resource: resource name
        :returns: resource manager instance
        :rtype: subclass of ResourceManager

        """
        raise NotImplementedError


class JSONRequests(object):

    def __init__(self, base_url, client=requests):
        self.base_url = base_url
        self._client = client

    def url(self, path):
        """Builds the absolute url from the path

        :param str path: path section of the url
        :returns: absolute url with base_url and path
        :rtype: string

        """
        return '{}{}'.format(self.base_url, path)

    def get(self, path, *args, **kwargs):
        """Sends a get request and returns response

        Raises a JSONRequestError in case the response is not 200

        :param str path: url path
        :returns: response of the get request
        :rtype: list or dict (deserialized json)

        """
        r = self._client.get(self.url(path))
        if r.status_code == 200:
            return r.json()
        else:
            raise JSONRequestError(r)

    def post(self, path, data, *args, **kwargs):
        """Sends a post request and returns the response

        :param str path: url path
        :param data: data to send in the post request
        :type data: list of dict (or anything json serializable)
        :returns: response of the post request
        :rtype: list or dict (deserialized json)

        """
        r = self._client.post(self.url(path), data=json.dumps(data),
                              headers={'content-type': 'application/json'},
                              *args, **kwargs)
        if r.status_code in {200, 201}:
            return r.json()
        else:
            raise JSONRequestError(r)

    def put(self, path, data, *args, **kwargs):
        """Sends a put request and returns the response

        :param str path: url path
        :param data: data to send in the put request
        :type data: list of dict (or anything json serializable)
        :returns: response of the put request
        :rtype: list or dict (deserialized json)

        """
        r = self._client.post(self.url(path), data=json.dumps(data),
                              headers={'content-type': 'application/json'}
                              *args, **kwargs)
        if r.status_code in {200, 201}:
            return r.json()
        else:
            raise JSONRequestError(r)

    def delete(self, path):
        """Sends a delete request to the API

        :param str path: url path
        :returns: Nothing
        :rtype: NoneType

        """
        self._client.delete(self.url(path))


class JSONRequestError(Exception):

    def __init__(self, response):
        """Request error exception for JSON requests

        Raised when the frontend api responds with a non desirable
        status code

        :param response: response object (from requests lib)

        """
        try:
            resp = response.json()
        except ValueError:
            reason = 'The API endpoint responded with an error'
        else:
            reason = resp.get('reason', 'The API endpoint responded with an error')
        msg = '{} ({})'.format(reason, response.status_code)
        Exception.__init__(self, msg)


def cc_to_uc(s):
    """Converts a CamelCase string to underscore or snake_case

    :param str s: CamelCase string
    :returns: snake_case string
    :rtype: str

    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
