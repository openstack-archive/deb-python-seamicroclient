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
from seamicroclient.v2 import servers


cs = fakes.FakeClient()


class ServersTest(utils.TestCase):

    def test_list_servers(self):
        sl = cs.servers.list()
        cs.assert_called('GET', '/servers')
        [self.assertTrue(isinstance(s, servers.Server)) for s in sl]

    def test_get_server(self):
        s = cs.servers.get(1)
        cs.assert_called('GET', '/servers/1')
        self.assertTrue(isinstance(s, servers.Server))

    def test_server_power_on(self):
        cs.servers.power_on(1)
        cs.assert_called('PUT', '/servers/1')

    def test_server_power_off(self):
        cs.servers.power_off(1)
        cs.assert_called('PUT', '/servers/1?action=power-off')

    def test_server_reset(self):
        cs.servers.reset(1)
        cs.assert_called('PUT', '/servers/1')

    def test_server_set_tagged_vlan(self):
        cs.servers.set_tagged_vlan(1, '12-12')
        cs.assert_called('PUT', '/servers/1/nic/0/taggedVlans')

    def test_server_unset_tagged_vlan(self):
        cs.servers.unset_tagged_vlan(1, '12-12')
        cs.assert_called('PUT', '/servers/1/nic/0/taggedVlans')

    def test_server_set_untagged_vlan(self):
        cs.servers.set_untagged_vlan(1, '12-12')
        cs.assert_called('PUT', '/servers/1/nic/0/untaggedVlans')

    def test_server_unset_untagged_vlan(self):
        cs.servers.unset_untagged_vlan(1, '12-12')
        cs.assert_called('PUT', '/servers/1/nic/0/untaggedVlans')

    def test_server_attach_volume_default(self):
        cs.servers.attach_volume(1, '1/p6-6/vol1')
        cs.assert_called('PUT', '/servers/1/vdisk/0')

    def test_server_attach_volume_with_vdisk(self):
        cs.servers.attach_volume(1, '1/p6-6/vol1', vdisk=3)
        cs.assert_called('PUT', '/servers/1/vdisk/3')

    def test_server_detach_volume(self):
        cs.servers.detach_volume(1, vdisk=0)
        cs.assert_called('DELETE', '/servers/1/vdisk/0')

    def test_set_boot_order(self):
        cs.servers.set_boot_order(1, 'pxe')
        cs.assert_called('PUT', '/servers/1')
