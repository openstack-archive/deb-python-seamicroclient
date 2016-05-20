# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Seamicro Client interface. Handles the REST calls and responses.
"""

import logging
import time

import requests

try:
    import json
except ImportError:
    import simplejson as json

from seamicroclient import exceptions
from seamicroclient import utils


class HTTPClient(object):

    USER_AGENT = 'python-seamicroclient'

    def __init__(self, user, password, auth_url=None,
                 timeout=None, http_log_debug=False, retries=3):
        self.user = user
        self.password = password
        self.api_endpoint = auth_url
        self.auth_url = auth_url.rstrip('/')
        self.version = 'v2.0'
        self.http_log_debug = http_log_debug
        if timeout is not None:
            self.timeout = float(timeout)
        else:
            self.timeout = None
        self.retries = int(retries)

        self.times = []  # [("item", starttime, endtime), ...]

        self._logger = logging.getLogger(__name__)
        if self.http_log_debug and not self._logger.handlers:
            # Logging level is already set on the root logger
            ch = logging.StreamHandler()
            self._logger.addHandler(ch)
            self._logger.propagate = False
            if hasattr(requests, 'logging'):
                rql = requests.logging.getLogger(requests.__name__)
                rql.addHandler(ch)
                # Since we have already setup the root logger on debug, we
                # have to set it up here on WARNING (its original level)
                # otherwise we will get all the requests logging messanges
                rql.setLevel(logging.WARNING)

    def get_timings(self):
        return self.times

    def reset_timings(self):
        self.times = []

    def http_log_req(self, method, url, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']

        string_parts.append(" '%s'" % url)
        string_parts.append(' -X %s' % method)

        for element in kwargs['headers']:
            header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
            string_parts.append(header)

        if 'data' in kwargs:
            string_parts.append(" -d '%s'" % (kwargs['data']))
        self._logger.debug("\nREQ: %s\n" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return
        self._logger.debug(
            "RESP: [%s] %s\nRESP BODY: %s\n",
            resp.status_code,
            resp.headers,
            resp.text)

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = 'application/json'
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        self.http_log_req(method, url, kwargs)
        resp = requests.request(
            method,
            url,
            **kwargs)
        self.http_log_resp(resp)

        if resp.text:
            # httplib2 returns a connection refused event as a 400 response.
            # To determine if it is a bad request or refused connection we need
            # to check the body.  httplib2 tests check for 'Connection refused'
            # or 'actively refused' in the body, so that's what we'll do.
            if resp.status_code == 400:
                if ('Connection refused' in resp.text or
                        'actively refused' in resp.text):
                    raise exceptions.ConnectionRefused(resp.text)
            try:
                body = json.loads(resp.text)
            except ValueError:
                body = resp.text
        else:
            body = None

        if resp.status_code >= 400:
            raise exceptions.from_response(resp, body, url, method)

        return resp, body

    def _time_request(self, url, method, **kwargs):
        start_time = time.time()
        resp, body = self.request(url, method, **kwargs)
        self.times.append(("%s %s" % (method, url),
                           start_time, time.time()))
        return resp, body

    def _cs_request(self, url, method, **kwargs):
        attempts = 0
        retry_delay = 5
        while True:
            attempts += 1
            if method in ['GET', 'DELETE']:
                url = "%s?username=%s&password=%s" % (url, self.user,
                                                      self.password)
            else:
                kwargs.setdefault('body', {}).update({'username': self.user,
                                                    'password': self.password})
            try:
                resp, body = self._time_request(self.api_endpoint + url,
                                                method, **kwargs)
                return resp, body
            except requests.exceptions.ConnectionError as e:
                if attempts > self.retries:
                    raise
                # Catch a connection refused from requests.request
                # retry again with some time delay
                self._logger.debug("Connection refused: %s" % e)
                self._logger.debug("Failed attempt(%s of %s), "
                                   "retrying in %s seconds" %
                                   (attempts, self.retries,
                                    retry_delay))
                time.sleep(retry_delay)

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)


def get_client_class(version):
    version_map = {
        '2': 'seamicroclient.v2.client.Client',
    }
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = "Invalid client version '%s'. must be one of: %s" % (
              (version, ', '.join(version_map.keys())))
        raise exceptions.UnsupportedVersion(msg)

    return utils.import_class(client_path)


def Client(version, *args, **kwargs):
    client_class = get_client_class(version)
    return client_class(*args, **kwargs)
