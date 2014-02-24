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
Scard interface.
"""

from seamicroclient import base


class Scard(base.Resource):
    HUMAN_ID = True

    def set_management_mode(self, mode, force=False, **kwargs):
        return self.manager.set_management_mode(self, mode, force, **kwargs)

    def volume_mode(self, value, **kwargs):
        if value:
            return self.manager.set_management_mode(self, 'volume', **kwargs)
        else:
            return self.manager.set_management_mode(self, 'disk', **kwargs)


class ScardManager(base.ManagerWithFind):
    resource_class = Scard

    def list(self, filters=None):
        """
        Get a list of scard properties.

        :rtype: list of :class:`Scard`
        """
        return self._list("/chassis/scard", filters=filters)

    def get(self, scard, **kwargs):
        """
        Get a specific scard.

        :rtype: Instance of :class:`Scard`
        """
        return self._get(base.getid(scard),
                         '/chassis/scard/%s' % base.getid(scard))

    def set_management_mode(self, scard, mode, force=False, **kwargs):
        """
        Set management mode of the specified scard
        """
        url = "/chassis/scard/%s/mgmtMode" % base.getid(scard)
        body = {'value': mode}
        return self.api.client.put(url, body=body)
