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
from seamicroclient.v2 import pools


cs = fakes.FakeClient()


class PoolsTest(utils.TestCase):

    def test_list_pools(self):
        pl = cs.pools.list()
        cs.assert_called('GET', '/storage/pools')
        [self.assertTrue(isinstance(s, pools.Pool)) for s in pl]

    def test_get_pool(self):
        p = cs.pools.get(1)
        cs.assert_called('GET', '/storage/pools/1')
        self.assertTrue(isinstance(p, pools.Pool))

    def test_create_pool(self):
        cs.pools.create(1, "pool-name", [1, 5, 6])
        cs.assert_called('PUT', '/storage/pools/1/pool-name')

    def test_delete_pool(self):
        cs.pools.delete('1/pool-name')
        cs.assert_called('DELETE', '/storage/pools/1/pool-name')

    def test_mount_pool(self):
        cs.pools.mount(1)
        cs.assert_called('PUT', '/storage/pools/1')

    def test_unmount_pool(self):
        cs.pools.unmount(1)
        cs.assert_called('PUT', '/storage/pools/1')
