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
FanTray interface.
"""

from seamicroclient import base


class FanTray(base.Resource):
    HUMAN_ID = True


class FanTrayManager(base.ManagerWithFind):
    resource_class = FanTray

    def get(self, fantray):
        """
        Get a fantray.

        :param fantray: ID of the :class:`FanTray` to get.
        :rtype: :class:`FanTray`
        """
        return self._get(base.getid(fantray),
                         "/chassis/fanTray/%s" % base.getid(fantray))

    def list(self, filters=None):
        """
        Get a list of fantray properties.

        :rtype: list of :class:`FanTray`
        """
        return self._list("/chassis/fanTray", filters=filters)
