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
from seamicroclient.v2 import chassis


cs = fakes.FakeClient()


class ChassisTest(utils.TestCase):

    def test_list_chassiss(self):
        sl = cs.chassis.list()
        cs.assert_called('GET', '/chassis')
        [self.assertTrue(isinstance(s, chassis.Chassis)) for s in sl]

    def test_chassis_write_mem(self):
        cs.chassis.writemem(1)
        cs.assert_called('PUT', '/chassis/system/writeMem')
