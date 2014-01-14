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

    def __repr__(self):
        return "<Pool: %s>" % self.id


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

    def list(self):
        """
        Get a list of pools.

        :rtype: list of :class:`Pool`
        """
        return self._list("/storage/pools")

    def _action(self, action, pool, info=None, **kwargs):
        """
        Perform a pool "action" -- .
        """
        body = {"action": action}
        body.update(info)
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/storage/pools/%s' % base.getid(pool)
        return self.api.client.put(url, body=body)
