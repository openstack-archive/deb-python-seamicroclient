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

    def no_shutdown(self, **kwargs):
        return self.manager.no_shutdown(self, **kwargs)

    def add_tagged_vlan(self, vlan_id, **kwargs):
        return self.manager.add_tagged_vlan(self, vlan_id, **kwargs)

    def remove_tagged_vlan(self, vlan_id, **kwargs):
        return self.manager.remove_tagged_vlan(self, vlan_id, **kwargs)

    def add_untagged_vlan(self, vlan_id, **kwargs):
        return self.manager.add_untagged_vlan(self, vlan_id, **kwargs)

    def remove_untagged_vlan(self, vlan_id, **kwargs):
        return self.manager.remove_untagged_vlan(self, vlan_id, **kwargs)


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

    def no_shutdown(self, interface, **kwargs):
        """
        Start the specified network Interface
        """
        url = "/interfaces/%s/shutdown" % base.getid(interface)
        body = {'value': False}
        return self.api.client.put(url, body=body)

    def add_tagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Add tagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/taggedVlans' % base.getid(interface)
        if isinstance(vlan_id, list):
            vlan_id = map(lambda x: str(x), vlan_id)
            body = {'add': ','.join(vlan_id)}
        else:
            body = {'add': str(vlan_id)}
        return self.api.client.put(url, body=body)

    def remove_tagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Remove tagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/taggedVlans' % base.getid(interface)
        body = {'remove': str(vlan_id)}
        return self.api.client.put(url, body=body)

    def add_untagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Add untagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/untaggedVlans' % base.getid(interface)
        body = {'add': str(vlan_id)}
        return self.api.client.put(url, body=body)

    def remove_untagged_vlan(self, interface, vlan_id, **kwargs):
        """
        Remove untagged vlan for the given Interface
        """
        url = '/interfaces/%s/vlans/untaggedVlans' % base.getid(interface)
        body = {'remove': str(vlan_id)}
        return self.api.client.put(url, body=body)
