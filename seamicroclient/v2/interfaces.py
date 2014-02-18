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
Interfaces object.
"""

from seamicroclient import base


class Interface(base.Resource):
    HUMAN_ID = True

    def shutdown(self, **kwargs):
        return self.manager.shutdown(self, **kwargs)

    def start(self, **kwargs):
        return self.manager.start(self, **kwargs)

    def create_tagged_vlan(self, vlan_id, **kwargs):
        return self.manager.create_tagged_vlan(self, vlan_id, **kwargs)

    def delete_tagged_vlan(self, vlan_id, **kwargs):
        return self.manager.delete_tagged_vlan(self, vlan_id, **kwargs)


class InterfaceManager(base.ManagerWithFind):
    resource_class = Interface

    def get(self, interface):
        """
        Get a interface.

        :param interface: ID of the :class:`Interface` to get.
        :rtype: :class:`Interface`
        """
        return self._get(base.getid(interface),
                         "/interfaces/%s" % base.getid(interface))

    def list(self, filters=None):
        """
        Get a list of interfaces.

        :rtype: list of :class:`Interface`
        """
        return self._list("/interfaces", filters=filters)

    def shutdown(self, interface, **kwargs):
        """
        Shutdown the specified network Interface
        """
        url = "/interfaces/%s/shutdown" % base.getid(interface)
        body = {'value': True}
        return self.api.client.put(url, body=body)

    def start(self, interface, **kwargs):
        """
        Start the specified network Interface
        """
        url = "/interfaces/%s/shutdown" % base.getid(interface)
        body = {'value': False}
        return self.api.client.put(url, body=body)

    def create_tagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Create tagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/taggedVlans' % base.getid(interface)
        body = {'value': str(vlan_id)}
        return self.api.client.put(url, body)

    def delete_tagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Create tagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/taggedVlans' % base.getid(interface)
        body = {'remove': str(vlan_id)}
        return self.api.client.put(url, body)

    def create_untagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Create untagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/untaggedVlans' % base.getid(interface)
        body = {'value': str(vlan_id)}
        return self.api.client.put(url, body)

    def delete_untagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Create untagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/untaggedVlans' % base.getid(interface)
        body = {'remove': str(vlan_id)}
        return self.api.client.put(url, body)
