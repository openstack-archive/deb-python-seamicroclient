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

"""
SMCard interface.
"""

from seamicroclient import base


class SMCard(base.Resource):
    HUMAN_ID = True


class SMCardManager(base.ManagerWithFind):
    resource_class = SMCard

    def get(self, smcard):
        """
        Get a smcard.

        :param smcard: ID of the :class:`SMCard` to get.
        :rtype: :class:`SMCard`
        """
        return self._get(base.getid(smcard),
                         "/chassis/smcard/%s" % base.getid(smcard))

    def list(self, filters=None):
        """
        Get a list of smcard properties.

        :rtype: list of :class:`SMCard`
        """
        return self._list("/chassis/smcard", filters=filters)
