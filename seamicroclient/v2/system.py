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
System interface.
"""

from seamicroclient import base


class System(base.Resource):
    HUMAN_ID = True

    def switchover(self, mxcard=None, **kwargs):
        return self.manager.switchover(self, mxcard, **kwargs)

    def writemem(self, **kwargs):
        return self.manager.writemem(self, **kwargs)

    def add_segment(self, vlan_id, **kwargs):
        return self.manager.add_segment(self, vlan_id, **kwargs)

    def remove_segment(self, vlan_id, **kwargs):
        return self.manager.remove_segment(self, vlan_id, **kwargs)

class SystemManager(base.ManagerWithFind):
    resource_class = System

    def list(self, filters=None):
        """
        Get a list of system properties.

        :rtype: list of :class:`System`
        """
        return self._list("/chassis/system", filters=filters)

    def switchover(self, system, mxcard=None, **kwargs):
        """
        Switchover system to different mxcard
        """
        url = "/chassis/system/switchover"
        body = {}
        if mxcard is not None:
            body = {'newActive': mxcard}
        return self.api.client.put(url, body=body)

    def writemem(self, system, **kwargs):
        """
        Write current system config to flash memory
        This will persist even after reboot of chassis
        """
        url = "/chassis/system/writeMem"
        return self.api.client.put(url, body={})

    def reload(self, system, **kwargs):
        """
        Reload the chassis and start the boot image
        """
        url = "/chassis/system/reload"
        return self.api.client.put(url, body={})

    def add_segment(self, system, vlan_id, **kwargs):
        """
        Create Global Network
        """
        url = "/chassis/system/vlans"
        if vlan_id is not None:
            action_params = {}
            action_params.update({'add': vlan_id})
            self.run_hooks('modify_body_for_action', action_params, **kwargs)
            return self.api.client.put(url, body=action_params)

    def remove_segment(self, system, vlan_id, **kwargs):
        """
        Remove Global Network
        """
        url = "/chassis/system/vlans"
        if vlan_id is not None:
            action_params = {}
            action_params.update({'remove': vlan_id})
            self.run_hooks('modify_body_for_action', action_params, **kwargs)
            return self.api.client.put(url, body=action_params)
