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
from seamicroclient.v2 import interfaces


cs = fakes.FakeClient()


class InterfacesTest(utils.TestCase):

    def test_list_interfaces(self):
        sl = cs.interfaces.list()
        cs.assert_called('GET', '/interfaces')
        [self.assertTrue(isinstance(s, interfaces.Interface)) for s in sl]

    def test_interface_get(self):
        cs.interfaces.get(1)
        cs.assert_called('GET', '/interfaces/1')

    def test_interface_shutdown(self):
        cs.interfaces.shutdown(1)
        cs.assert_called('PUT', '/interfaces/1/shutdown')

    def test_interface_no_shutdown(self):
        cs.interfaces.no_shutdown(1)
        cs.assert_called('PUT', '/interfaces/1/shutdown')

    def test_interface_add_taggedvlan_list(self):
        cs.interfaces.add_tagged_vlan(1, [1, 2, 3])
        cs.assert_called('PUT', '/interfaces/1/vlans/taggedVlans')

    def test_interface_add_taggedvlan_single(self):
        cs.interfaces.add_tagged_vlan(1, '23-25')
        cs.assert_called('PUT', '/interfaces/1/vlans/taggedVlans')

    def test_interface_remove_taggedvlan(self):
        cs.interfaces.remove_tagged_vlan(1, '23-25')
        cs.assert_called('PUT', '/interfaces/1/vlans/taggedVlans')

    def test_interface_add_untaggedvlan(self):
        cs.interfaces.add_untagged_vlan(1, '23')
        cs.assert_called('PUT', '/interfaces/1/vlans/untaggedVlans')

    def test_interface_remove_untaggedvlan(self):
        cs.interfaces.remove_untagged_vlan(1, '23')
        cs.assert_called('PUT', '/interfaces/1/vlans/untaggedVlans')
