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

import json

import mock
import requests


from seamicroclient import client
from seamicroclient import exceptions
from seamicroclient.tests import utils


fake_response = utils.TestResponse({
    "status_code": 200,
    "text": '{"hi": "there"}',
})
mock_request = mock.Mock(return_value=(fake_response))

refused_response = utils.TestResponse({
    "status_code": 400,
    "text": '[Errno 111] Connection refused',
})
refused_mock_request = mock.Mock(return_value=(refused_response))

bad_req_response = utils.TestResponse({
    "status_code": 400,
    "text": '',
})
bad_req_mock_request = mock.Mock(return_value=(bad_req_response))


def get_client():
    cl = client.HTTPClient("username", "password", "http://example.com")
    return cl


def get_authed_client():
    cl = get_client()
    cl.auth_url = "http://example.com"
    cl.auth_token = "token"
    cl.user = "user"
    cl.password = "password"
    return cl


class ClientTest(utils.TestCase):

    def test_get(self):
        cl = get_authed_client()

        @mock.patch.object(requests.Session, "request", mock_request)
        @mock.patch('time.time', mock.Mock(return_value=1234))
        def test_get_call():
            resp, body = cl.get("/hi")
            headers = {'Accept': 'application/json',
                       'User-Agent': 'python-seamicroclient'}
            mock_request.assert_called_with(
                "GET",
                "http://example.com/hi?username=%s&password=%s" % (cl.user,
                                                                cl.password),
                headers=headers)
            # Automatic JSON parsing
            self.assertEqual(body, {"hi": "there"})

        test_get_call()

    def test_post(self):
        cl = get_authed_client()

        @mock.patch.object(requests.Session, "request", mock_request)
        def test_post_call():
            body = {'k1': 'v1', 'k2': 'v2', 'authtoken': cl.auth_token}
            cl.post("/hi", body=body)
            headers = {'Content-Type': 'application/json', 'Accept':
                       'application/json',
                       'User-Agent': 'python-seamicroclient'}
            mock_request.assert_called_with(
                "POST",
                "http://example.com/hi",
                headers=headers,
                data=json.dumps(body))

        test_post_call()

    def test_connection_refused(self):
        cl = get_client()

        @mock.patch.object(requests.Session, "request", refused_mock_request)
        def test_refused_call():
            self.assertRaises(exceptions.ConnectionRefused, cl.get, "/hi")

        test_refused_call()

    def test_bad_request(self):
        cl = get_client()

        @mock.patch.object(requests.Session, "request", bad_req_mock_request)
        def test_refused_call():
            self.assertRaises(exceptions.BadRequest, cl.get, "/hi")

        test_refused_call()

    def test_client_logger(self):
        cl1 = client.HTTPClient("username", "password",
                                "http://example.com",
                                http_log_debug=True)
        self.assertEqual(len(cl1._logger.handlers), 1)

        cl2 = client.HTTPClient("username", "password",
                                "http://example.com",
                                http_log_debug=True)
        self.assertEqual(len(cl2._logger.handlers), 1)
