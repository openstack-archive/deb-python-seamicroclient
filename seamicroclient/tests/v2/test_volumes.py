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
from seamicroclient.v2 import volumes


cs = fakes.FakeClient()


class VolumesTest(utils.TestCase):

    def test_list_volumes(self):
        vl = cs.volumes.list()
        cs.assert_called('GET', '/storage/volumes')
        [self.assertTrue(isinstance(s, volumes.Volume)) for s in vl]

    def test_get_volume(self):
        p = cs.volumes.get(1)
        cs.assert_called('GET', '/storage/volumes/1')
        self.assertTrue(isinstance(p, volumes.Volume))

    def test_create_volume(self):
        v = cs.volumes.create(2, '0/p0_0', '1')
        cs.assert_called('PUT', '/storage/volumes/0/p0_0/1')
        self.assertTrue(isinstance(v, volumes.Volume))
