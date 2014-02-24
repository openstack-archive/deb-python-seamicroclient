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
from seamicroclient.v2 import disks


cs = fakes.FakeClient()


class DisksTest(utils.TestCase):

    def test_list_disks(self):
        sl = cs.disks.list()
        cs.assert_called('GET', '/storage/disks')
        [self.assertTrue(isinstance(s, disks.Disk)) for s in sl]

    def test_get_disk(self):
        s = cs.disks.get(1)
        cs.assert_called('GET', '/storage/disks/1')
        self.assertTrue(isinstance(s, disks.Disk))

    def test_disk_power_on(self):
        cs.disks.power_on(1)
        cs.assert_called('PUT', '/storage/disks/1')

    def test_disk_power_off(self):
        cs.disks.power_off(1)
        cs.assert_called('PUT', '/storage/disks/1')

    def test_disk_activate_led(self):
        cs.disks.activate_led(1)
        cs.assert_called('PUT', '/storage/disks/1')

    def test_disk_deactivate_lef(self):
        cs.disks.deactivate_led(1)
        cs.assert_called('PUT', '/storage/disks/1')
