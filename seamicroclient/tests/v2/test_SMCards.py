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
from seamicroclient.v2 import smcards


cs = fakes.FakeClient()


class SMCardstest(utils.TestCase):

    def test_list_smcards(self):
        pl = cs.smcards.list()
        cs.assert_called('GET', '/chassis/smcard')
        [self.assertTrue(isinstance(s, smcards.SMCard)) for s in pl]

    def test_get_smcards(self):
        p = cs.smcards.get(1)
        cs.assert_called('GET', '/chassis/smcard/1')
        self.assertTrue(isinstance(p, smcards.SMCard))
