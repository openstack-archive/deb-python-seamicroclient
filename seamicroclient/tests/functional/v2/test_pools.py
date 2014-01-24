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
import uuid

from seamicroclient.tests import utils
from seamicroclient.v2 import Client


cs = Client("admin", "seamicro", "http://chassis/v2.0")


class PoolsTest(utils.TestCase):

    def test_list_pool(self):
        pool_list = cs.pools.list()
        self.assertTrue(len(pool_list) > 0)

    def test_list_pool_with_filter(self):
        filters = {'id': 'p6-'}
        for pool in cs.pools.list(filters):
            for k, v in filters.iteritems():
                self.assertIn(v, getattr(pool, k))

    def test_list_pool_with_filter_no_match(self):
        filters = {'id': str(uuid.uuid4())}
        for pool in cs.pools.list(filters):
            for k, v in filters.iteritems():
                self.assertNotIn(getattr(pool, k), v)

    def test_get_pool(self):
        pool_id = cs.pools.list()[0].id
        pool = cs.pools.get(pool_id)
        self.assertEqual(pool.id, pool_id)
