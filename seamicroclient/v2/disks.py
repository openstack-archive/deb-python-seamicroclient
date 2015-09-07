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
Disks interface.
"""

from seamicroclient import base


class Disk(base.Resource):
    HUMAN_ID = True

    def power_on(self, **kwargs):
        return self.manager.power_on(self, **kwargs)

    def power_off(self, **kwargs):
        return self.manager.power_off(self, **kwargs)

    def active_led(self, **kwargs):
        return self.manager.active_led(self, **kwargs)

    def deactivate_led(self, **kwargs):
        return self.manager.deactivate_led(self, **kwargs)


class DiskManager(base.ManagerWithFind):
    resource_class = Disk

    def get(self, disk):
        """
        Get a disk.

        :param disk: ID of the :class:`Disk` to get.
        :rtype: :class:`Disk`
        """
        return self._get(base.getid(disk),
                         "/storage/disks/%s" % base.getid(disk))

    def list(self, filters=None):
        """
        Get a list of disks.

        :rtype: list of :class:`Disk`
        """
        return self._list("/storage/disks", filters=filters)

    def power_off(self, disk, **kwargs):
        """
        Power off the specified Disk
        """
        url = "/storage/disks/%s" % base.getid(disk)
        body = {'action': 'power-off'}
        return self.api.client.put(url, body=body)

    def power_on(self, disk, **kwargs):
        """
        Power on the specified Disk
        """
        url = "/storage/disks/%s" % base.getid(disk)
        body = {'action': 'power-on'}
        return self.api.client.put(url, body=body)

    def activate_led(self, disk, **kwargs):
        """
        Activate LED of the specified Disk
        """
        url = "/storage/disks/%s" % base.getid(disk)
        body = {'action': 'activate-led'}
        return self.api.client.put(url, body=body)

    def deactivate_led(self, disk, **kwargs):
        """
        De-activate LED of the specified Disk
        """
        url = "/storage/disks/%s" % base.getid(disk)
        body = {'action': 'deactivate-led'}
        return self.api.client.put(url, body=body)
