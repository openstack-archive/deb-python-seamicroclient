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
import time

from seamicroclient.tests import utils
from seamicroclient.v2 import Client


STATUS_WAIT_TIMEOUT = 30
BUILD_INTERVAL = 10

SERVER_ID = '0/0'
UNTAGGED_VLAN_ID = '7'
TAGGED_VLAN_ID = '17'

cs = Client("admin", "seamicro", "http://chassis/v2.0")


class FunctionalException(Exception):
    pass


class ServersTest(utils.TestCase):

    @staticmethod
    def wait_for_server_status(s, active):
        start_time = int(time.time())
        while True:
            timed_out = int(time.time()) - start_time > STATUS_WAIT_TIMEOUT
            if timed_out:
                raise FunctionalException()
            time.sleep(BUILD_INTERVAL)
            s = s.refresh()
            if s.active == active:
                return

    @staticmethod
    def create_volume(size=1):
        pool = cs.pools.list()[0]
        return cs.volumes.create(size, pool)

    def test_list_servers(self):
        sl = cs.servers.list()
        self.assertTrue(len(sl) > 0)

    def test_get_server(self):
        s = cs.servers.get(SERVER_ID)
        self.assertEqual(s.id, SERVER_ID)

    def test_power_on_power_off(self):
        s = cs.servers.get(SERVER_ID)
        self.assertEqual(s.id, SERVER_ID)
        if s.active:
            s.power_off()
            self.wait_for_server_status(s, active=False)
            s = s.refresh()
            self.assertEqual(s.active, False)
            s.power_on()
        else:
            s.power_on()
            self.wait_for_server_status(s, active=True)
            s = s.refresh()
            self.assertEqual(s.active, True)
            s.power_off()

    def test_reset(self):
        s = cs.servers.get(SERVER_ID)
        self.assertEqual(s.id, SERVER_ID)
        s.reset()
        self.wait_for_server_status(s, active=True)
        s = s.refresh()
        self.assertEqual(s.active, True)

    def test_attach_detach_volume(self):
        volume_id = self.create_volume()
        server = cs.servers.list()[0]
        server.detach_volume()
        server.attach_volume(volume_id)
        server = server.refresh()
        self.assertEqual(server.vdisk['0'], volume_id)
        server.detach_volume()
        cs.volumes.delete(volume_id)

    def test_set_tagged_vlan(self):
        server = cs.servers.list()[0]
        server.unset_tagged_vlan(TAGGED_VLAN_ID)
        server = server.refresh(10)
        server.set_tagged_vlan(TAGGED_VLAN_ID)
        server = server.refresh(10)
        self.assertTrue(TAGGED_VLAN_ID in server.nic['0']['taggedVlan'])
        server.unset_tagged_vlan(TAGGED_VLAN_ID)

    def test_unset_tagged_vlan(self):
        server = cs.servers.list()[0]
        server.unset_tagged_vlan(TAGGED_VLAN_ID)
        server = server.refresh(10)
        server.set_tagged_vlan(TAGGED_VLAN_ID)
        server = server.refresh(10)
        server.unset_tagged_vlan(TAGGED_VLAN_ID)
        server = server.refresh(10)
        self.assertTrue(TAGGED_VLAN_ID not in server.nic['0']['taggedVlan'])

    def test_unset_untagged_vlan(self):
        server = cs.servers.list()[0]
        server.unset_untagged_vlan(UNTAGGED_VLAN_ID)
        server = server.refresh(10)
        server.set_untagged_vlan(UNTAGGED_VLAN_ID)
        server = server.refresh(10)
        server.unset_untagged_vlan(UNTAGGED_VLAN_ID)
        server = server.refresh(10)
        self.assertTrue(UNTAGGED_VLAN_ID not in
                        server.nic['0']['untaggedVlan'])

    def test_set_untagged_vlan(self):
        server = cs.servers.list()[0]
        server.unset_untagged_vlan(UNTAGGED_VLAN_ID)
        server = server.refresh(10)
        server.set_untagged_vlan(UNTAGGED_VLAN_ID)
        server = server.refresh(10)
        self.assertTrue(UNTAGGED_VLAN_ID in server.nic['0']['untaggedVlan'])
        server.unset_untagged_vlan(UNTAGGED_VLAN_ID)
