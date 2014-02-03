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


class VolumesTest(utils.TestCase):

    @staticmethod
    def create_volume(volume_size=2, pool=None):
        return cs.volumes.create(volume_size, pool)

    def test_list_volume(self):
        volume_list = cs.volumes.list()
        self.assertTrue(len(volume_list) > 0)

    def test_get_volume(self):
        volume_id = cs.volumes.list()[0].id
        volume = cs.volumes.get(volume_id)
        self.assertEqual(volume.id, volume_id)

    def test_create_volume(self):
        pool = cs.pools.list()[0]
        volume_size = 2
        volume_id = self.create_volume(volume_size, pool)
        self.assertIn(pool.id, volume_id)
        cs.volumes.delete(volume_id)

    def test_delete_volume(self):
        pool = cs.pools.list()[0]
        volume = self.create_volume(pool=pool)
        cs.volumes.delete(volume)
        volume = cs.volumes.get(volume)
        self.assertEqual(volume.actualSize, 0)
