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
Pool interface.
"""


from seamicroclient import base


class Pool(base.Resource):
    HUMAN_ID = True

    def delete(self, **kwargs):
        return self.manager.delete(self, **kwargs)

    def mount(self, **kwargs):
        return self.manager.mount(self, **kwargs)


class PoolManager(base.ManagerWithFind):
    resource_class = Pool

    def get(self, pool):
        """
        Get a pool.

        :param pool: ID of the :class:`Pool` to get.
        :rtype: :class:`Pool`
        """
        return self._get(base.getid(pool),
                         "/storage/pools/%s" % base.getid(pool))

    def list(self, filters=None):
        """
        Get a list of pools.

        :rtype: list of :class:`Pool`
        """
        return self._list("/storage/pools", filters=filters)

    def create(self, slot, pool_name, disks, raid_level=0, **kwargs):
        """
        Create a pool on the given scard slot using disks of that slot.

        :rtype: Instance of :class:`Pool`
        """
        disks = map(lambda x: str(x), disks)
        body = {'disks': ','.join(disks), 'raidLevel': raid_level}
        url = '/storage/pools/%s/%s' % (base.getid(slot), pool_name)
        return self.api.client.put(url, body=body)

    def delete(self, pool, **kwargs):
        """
        Delete the specified pool.
        """
        url = '/storage/pools/%s' % base.getid(pool)
        return self.api.client.delete(url)

    def mount(self, pool, **kwargs):
        """
        Mount the specified Pool
        """
        return self._action("mount", pool, **kwargs)

    def unmount(self, pool, **kwargs):
        """
        UnMount the specified Pool
        """
        return self._action("unmount", pool, **kwargs)

    def _action(self, action, pool, info=None, **kwargs):
        """
        Perform a pool "action" -- .
        """
        body = {"action": action}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/storage/pools/%s' % base.getid(pool)
        return self.api.client.put(url, body=body)
