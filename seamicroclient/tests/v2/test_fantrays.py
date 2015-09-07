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
from seamicroclient.tests.v2 import fakes
from seamicroclient.v2 import fantrays


cs = fakes.FakeClient()


class FanTraysTest(utils.TestCase):

    def test_list_fantrays(self):
        sl = cs.fantrays.list()
        cs.assert_called('GET', '/chassis/fanTray')
        [self.assertTrue(isinstance(s, fantrays.FanTray)) for s in sl]

    def test_fantray_get(self):
        cs.fantrays.get(1)
        cs.assert_called('GET', '/chassis/fanTray/1')
