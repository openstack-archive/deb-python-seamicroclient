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
PowerSupply interface.
"""

from seamicroclient import base


class PowerSupply(base.Resource):
    HUMAN_ID = True


class PowerSupplyManager(base.ManagerWithFind):
    resource_class = PowerSupply

    def get(self, powersupply):
        """
        Get a powersupply.

        :param powersupply: ID of the :class:`PowerSupply` to get.
        :rtype: :class:`PowerSupply`
        """
        return self._get(base.getid(powersupply),
                         "/chassis/powersupply/%s" % base.getid(powersupply))

    def list(self, filters=None):
        """
        Get a list of powersupply properties.

        :rtype: list of :class:`PowerSupply`
        """
        return self._list("/chassis/powersupply", filters=filters)
