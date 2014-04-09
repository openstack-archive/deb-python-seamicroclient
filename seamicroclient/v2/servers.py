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
Server interface.
"""

from seamicroclient import base


TAGGED_VLAN = "taggedVlans"
UNTAGGED_VLAN = "untaggedVlans"


class Server(base.Resource):
    HUMAN_ID = True

    def power_on(self, using_pxe=False):
        self.manager.power_on(self, using_pxe)

    def power_off(self, force=False):
        self.manager.power_off(self, force)

    def reset(self, using_pxe=False):
        self.manager.reset(self, using_pxe)

    def set_tagged_vlan(self, vlan_id, **kwargs):
        self.manager.set_tagged_vlan(self, vlan_id, **kwargs)

    def unset_tagged_vlan(self, vlan_id, **kwargs):
        self.manager.unset_tagged_vlan(self, vlan_id, **kwargs)

    def set_untagged_vlan(self, vlan_id, **kwargs):
        self.manager.set_untagged_vlan(self, vlan_id, **kwargs)

    def unset_untagged_vlan(self, vlan_id, **kwargs):
        self.manager.unset_untagged_vlan(self, vlan_id, **kwargs)

    def attach_volume(self, volume, vdisk=0, **kwargs):
        self.manager.attach_volume(self, volume, vdisk, **kwargs)

    def detach_volume(self, vdisk=0, **kwargs):
        self.manager.detach_volume(self, vdisk, **kwargs)

    def set_boot_order(self, boot_order="hd0", **kwargs):
        self.manager.set_boot_order(self, boot_order, **kwargs)


class ServerManager(base.ManagerWithFind):
    resource_class = Server

    def get(self, server):
        """
        Get a server.

        :param server: ID of the :class:`Server` to get.
        :rtype: :class:`Server`
        """
        return self._get(base.getid(server),
                         "/servers/%s" % base.getid(server))

    def list(self):
        """
        Get a list of servers.

        :rtype: list of :class:`Server`
        """
        return self._list("/servers")

    def attach_volume(self, server, volume, vdisk=0, **kwargs):
        """
        Attach volume to vdisk # to given server

        :param server: The :class:`Server` (or its ID) to power on.
        :param volume: The :class:`Volume` (or its ID) that is to be attached.
        :param vdisk: The vdisk number of the server to attach volume to.
        :
        """
        body = {"value": volume}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/servers/%s/vdisk/%s' % (base.getid(server), vdisk)
        return self.api.client.put(url, body=body)

    def detach_volume(self, server, vdisk=0, **kwargs):
        """
        Detach volume attached to vdisk # of given server

        :param server: The :class:`Server` (or its ID) to power on.
        :param vdisk: The vdisk number of the server to detach volume to.
        :
        """
        url = '/servers/%s/vdisk/%s' % (base.getid(server), vdisk)
        return self._delete(url)

    def power_on(self, server, using_pxe=False, **kwargs):
        """
        Power on a server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param using_pxe: power on server and use pxe boot.
        """
        action_params = {}
        if using_pxe:
            action_params = {"using-pxe": using_pxe}
        self._action('power-on', server, action_params)

    def power_off(self, server, force=False, **kwargs):
        """
        Power off a server.

        :param server: The :class:`Server` (or its ID) to power off.
        :param force: force the server to power off.
        """
        action = 'power-off'
        url = '/servers/%s?action=%s' % (base.getid(server), action)
        if force:
            url = '%s&force=true' % url
        return self.api.client.put(url, body={})

    def reset(self, server, using_pxe=False, **kwargs):
        """
        Reset power of a server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param using_pxe: reset and power on server and use pxe boot.
        """
        action_params = {}
        if using_pxe:
            action_params = {"using-pxe": using_pxe}
        self._action('reset', server, action_params)

    def set_tagged_vlan(self, server, vlan_id, **kwargs):
        """
        Set the tagged vlan id for the server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param vlan_id: The tagged vlan id for the server.
        """
        self._handle_vlan(server, vlan_id, TAGGED_VLAN, **kwargs)

    def unset_tagged_vlan(self, server, vlan_id, **kwargs):
        """
        Unset the tagged vlan id for the server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param vlan_id: The tagged vlan id for the server.
        """
        self._handle_vlan(server, vlan_id, TAGGED_VLAN, unset=True, **kwargs)

    def set_untagged_vlan(self, server, vlan_id, **kwargs):
        """
        Set the untagged vlan id for the server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param vlan_id: The untagged vlan id for the server.
        """
        self._handle_vlan(server, vlan_id, UNTAGGED_VLAN, **kwargs)

    def unset_untagged_vlan(self, server, vlan_id, **kwargs):
        """
        Unset the untagged vlan id for the server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param vlan_id: The untagged vlan id for the server.
        """
        self._handle_vlan(server, vlan_id, UNTAGGED_VLAN,
                          unset=True, **kwargs)

    def _handle_vlan(self, server, vlan_id, vlan_type, unset=False, **kwargs):
        """
        Set/Unset tagged/untagged vlan id for the server.

        :param server: The :class:`Server` (or its ID) to power on.
        :param vlan_id: The tagged vlan id for the server.
        :param vlan_type: tagged-vlan or untagged-vlan type.
        :param unset: Boolean flag to unset the vlan_id for the server.
        """
        if vlan_id is not None:

            action_params = {}
            if unset:
                action_params.update({'remove': vlan_id})
            else:
                action_params.update({'add': vlan_id})
            self.run_hooks('modify_body_for_action', action_params, **kwargs)
            url = '/servers/%s/nic/0/%s' % (base.getid(server), vlan_type)
            return self.api.client.put(url, body=action_params)

    def set_boot_order(self, server, boot_order="hd0", **kwargs):
        """
        Set bios boot order for the server

        :param server: The :class:`Server` (or its ID)
        :param boot_order: The boot order for the server
        """
        action_params = {'boot-order': boot_order}
        if boot_order == "pxe":
            action_params.update({'boot-order': 'pxe,hd0'})

        return self._action('set-bios-boot-order', server, action_params)

    def _action(self, action, server, info=None, **kwargs):
        """
        Perform a server "action" -- power-on/power-off/reset/etc.
        """
        body = {"action": action}
        body.update(info)
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/servers/%s' % base.getid(server)
        return self.api.client.put(url, body=body)
