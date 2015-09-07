# Copyright 2012 OpenStack Foundation
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


import seamicroclient.client
from seamicroclient.tests import utils
import seamicroclient.v2.client


class ClientTest(utils.TestCase):

    def test_client_with_timeout(self):
        instance = seamicroclient.client.HTTPClient(user='user',
                                                    password='password',
                                                    timeout=2,
                                                    auth_url="http://test")
        self.assertEqual(instance.timeout, 2)

    def test_get_client_class_v2(self):
        output = seamicroclient.client.get_client_class('2')
        self.assertEqual(output, seamicroclient.v2.client.Client)
