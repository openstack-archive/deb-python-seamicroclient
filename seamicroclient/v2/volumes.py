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
Volume interface.
"""

import binascii
import os

from seamicroclient import base


class Volume(base.Resource):
    HUMAN_ID = True

    def delete(self):
        self.manager.delete(self)


class VolumeManager(base.ManagerWithFind):
    resource_class = Volume

    def get(self, volume):
        """
        Get a volume.

        :param volume: ID of the :class:`Volume` to get.
        :rtype: :class:`Volume`
        """
        return self._get(base.getid(volume),
                         "/storage/volumes/%s" % base.getid(volume))

    def list(self):
        """
        Get a list of volumes.

        :rtype: list of :class:`Volume`
        """
        return self._list("/storage/volumes")

    def create(self, size, pool, volume_id=None, **kwargs):
        """
        Create a volume of the given size in the given pool.

        :param volume_id: ID of the :class: `Volume` to create
        :param pool: Object  of the :class: `Pool` in which the volume will be
                     created.
        :param size: Size of the new volume in GB.
        """
        create_params = {}
        if volume_id is None:
            volume_id = str(binascii.b2a_hex(os.urandom(6)))
        if pool and volume_id and size:
            create_params = {'volume-size': str(size)}
            resource_url = "%s/%s" % (base.getid(pool), volume_id)
            return self._create(resource_url, create_params)

    def delete(self, volume):
        self._delete("/storage/volume/%s" % base.getid(volume))

    def _create(self, resource_url, body, **kwargs):
        """
        Create a volume
        """
        body.update({"action": "create"})
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/storage/volumes/%s' % resource_url
        return self._update(url, body=body)

    def _action(self, action, volume, info=None, **kwargs):
        """
        Perform a volume "action" -- .
        """
        body = {"action": action}
        body.update(info)
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/storage/volumes/%s' % base.getid(volume)
        return self.api.client.put(url, body=body)
