# -*- coding: utf-8 -*-
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

from seamicroclient.tests import utils
from seamicroclient.v2 import Client


cs = Client("admin", "seamicro", "http://chassis/v2.0")

class ServersTest(utils.TestCase):

    def test_list_servers(self):
        sl = cs.servers.list()
        self.assertTrue(len(sl) > 0)
