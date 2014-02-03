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
                 timeout=None, http_log_debug=False):
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

        self.times = []  # [("item", starttime, endtime), ...]

        self.auth_token = None

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
        # requests within the same session can reuse TCP connections from pool
        self.http = requests.Session()

    def unauthenticate(self):
        """Forget all of our authentication information."""
        self.auth_token = None

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
        resp = self.http.request(
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
        if self.auth_token:
            if method in ['GET', 'DELETE']:
                url = "%s?username=%s&password=%s" % (url, self.user,
                                                      self.password)
            else:
                kwargs.setdefault('body', {})['authtoken'] = self.auth_token

        # Perform the request once. If we get a 401 back then it
        # might be because the auth token expired, so try to
        # re-authenticate and try again. If it still fails, bail.
        try:

            resp, body = self._time_request(self.api_endpoint + url, method,
                                            **kwargs)
            return resp, body
        except (exceptions.Unauthorized, exceptions.BadRequest) as e:
            try:
                # first discard auth token, to avoid the possibly expired
                # token being re-used in the re-authentication attempt
                self.unauthenticate()
                self.authenticate()
                if method in ['GET', 'DELETE']:
                    url = "%s?username=%s&password=%s" % (url, self.user,
                                                          self.password)
                else:
                    kwargs.setdefault(
                        'body', {})['authtoken'] = self.auth_token

                resp, body = self._time_request(self.api_endpoint + url,
                                                method, **kwargs)
                return resp, body
            except exceptions.Unauthorized:
                raise e

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

    def authenticate(self):
        auth_url = self.auth_url
        if self.version == "v2.0":  # FIXME(rk): This should be better.
            self._v2_auth(auth_url)

    def _v2_auth(self, url):
        """Authenticate against a v2.0 auth service."""
        if self.auth_token:
            return
        else:
            body = {"username": self.user, "password": self.password}

        return self._authenticate(url, body)

    def _authenticate(self, url, body, **kwargs):
        """Authenticate and extract the service catalog."""
        method = "POST"
        token_url = url + "/login"

        # Make sure we follow redirects when trying to reach Keystone
        resp, respbody = self._time_request(
            token_url,
            method,
            body=body,
            allow_redirects=True,
            **kwargs)

        return self._extract_auth_token(url, resp, respbody)

    def _extract_auth_token(self, url, resp, body):
        if resp.status_code == 200 or resp.status_code == 201:
            if 'OpaqueRef' not in body:
                raise exceptions.AuthorizationFailure()
            self.auth_token = body


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
