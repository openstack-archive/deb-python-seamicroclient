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
VLAN_ID = '7'
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
            s = cs.servers.get(s.id)
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
            s = cs.servers.get(s.id)
            self.assertEqual(s.active, False)
            s.power_on()
        else:
            s.power_on()
            self.wait_for_server_status(s, active=True)
            s = cs.servers.get(s.id)
            self.assertEqual(s.active, True)
            s.power_off()

    def test_reset(self):
        s = cs.servers.get(SERVER_ID)
        self.assertEqual(s.id, SERVER_ID)
        s.reset()
        self.wait_for_server_status(s, active=True)
        s = cs.servers.get(SERVER_ID)
        self.assertEqual(s.active, True)

# skipping because vdisk info is not updated due to api bug in GET
# /servers/<server_id>
#    def test_attach_detach_volume(self):
#        volume_id = self.create_volume()
#        server = cs.servers.list()[0]
#        server.detach_volume()
#        server.attach_volume(volume_id)
#        server = cs.servers.get(server.id)
#        self.assertEqual(server.vdisk['0'], volume_id)
#        server.detach_volume()
#        cs.volumes.delete(volume_id)

    def test_set_unset_tagged_vlan(self):
        server = cs.servers.list()[0]
        server.set_tagged_vlan(VLAN_ID)
        server = cs.servers.get(server.id)
        self.assertIn(VLAN_ID, server.nic['0']['taggedVlans'])
        server.unset_tagged_vlan(VLAN_ID)
        server = cs.servers.get(server.id)
        self.assertNotIn(VLAN_ID, server.nic['0']['taggedVlans'])
