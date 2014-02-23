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
Chassis interface.
"""

from seamicroclient import base


class Chassis(base.Resource):
    HUMAN_ID = True

    def writemem(self, **kwargs):
        return self.manager.writemem(self, **kwargs)


class ChassisManager(base.ManagerWithFind):
    resource_class = Chassis

    def list(self, filters=None):
        """
        Get a list of chassis properties.

        :rtype: list of :class:`Chassis`
        """
        return self._list("/chassis", filters=filters)

    def writemem(self, chassis, **kwargs):
        """
        Write current chassis config to flash memory
        This will persist even after reboot of chassis
        """
        url = "/chassis/system/writeMem"
        return self.api.client.put(url, body={})
