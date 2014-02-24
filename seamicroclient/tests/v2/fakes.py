# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from seamicroclient import client as base_client
from seamicroclient.openstack.common.py3kcompat import urlutils
from seamicroclient.tests import fakes
from seamicroclient.tests import utils
from seamicroclient.v2 import client


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, *args, **kwargs):
        client.Client.__init__(self, 'username', 'password',
                               'auth_url')
        self.client = FakeHTTPClient(**kwargs)


class FakeHTTPClient(base_client.HTTPClient):

    def __init__(self, **kwargs):
        self.username = 'username'
        self.password = 'password'
        self.auth_url = 'auth_url'
        self.callstack = []
        self.timings = 'timings'
        self.http_log_debug = 'http_log_debug'

    def _cs_request(self, url, method, **kwargs):
        # Check that certain things are called correctly
        if method in ['GET', 'DELETE']:
            assert 'body' not in kwargs
        elif method == 'PUT':
            assert 'body' in kwargs

        # Call the method
        args = urlutils.parse_qsl(urlutils.urlparse(url)[4])
        kwargs.update(args)
        munged_url = url.rsplit('?', 1)[0]
        munged_url = munged_url.strip('/').replace('/', '_').replace('.', '_')
        munged_url = munged_url.replace('-', '_')
        munged_url = munged_url.replace(' ', '_')

        callback = "%s_%s" % (method.lower(), munged_url)

        if not hasattr(self, callback):
            raise AssertionError('Called unknown API method: %s %s, '
                                 'expected fakes method name: %s' %
                                 (method, url, callback))

        # Note the call
        self.callstack.append((method, url, kwargs.get('body', None)))

        status, headers, body = getattr(self, callback)(**kwargs)
        r = utils.TestResponse({
            "status_code": status,
            "text": body,
            "headers": headers,
        })
        return r, body

    def get_servers_1(self, **kwargs):
        return (200, {}, {'id': 1234, 'name': 'sample-server'}
                )

    def get_servers(self, **kwargs):
        return (200, {}, {'0/0': {}, '1/0': {}})

    def put_servers_1(self, **kwargs):
        return (200, {}, {})

    def put_servers_1_nic_0_untaggedVlans(self, **kwargs):
        return (200, {}, {})

    def put_servers_1_nic_0_taggedVlans(self, **kwargs):
        return (200, {}, {})

    def get_storage_pools(self):
        return (200, {}, {'0/p0-0': {}, '0/p1-1': {}})

    def get_storage_pools_1(self):
        return (200, {}, {'0/p0-0': {}})

    def get_storage_volumes(self):
        return (200, {}, {'0/p0-0/1': {}, '0/p1-1/1': {}})

    def get_storage_volumes_1(self):
        return (200, {}, {'1': {}})

    def put_storage_volumes_0_p0_0_1(self, **kwargs):
        return (200, {}, {'0/p0-0/1': {}})

    def get_storage_volumes_0_p0_0_1(self, **kwargs):
        return (200, {}, {'0/p0-0/1': {}})

    def put_servers_1_vdisk_0(self, **kwargs):
        return (200, {}, {})

    def put_servers_1_vdisk_3(self, **kwargs):
        return (200, {}, {})

    def delete_servers_1_vdisk_0(self, **kwargs):
        return (200, {}, {})

    def get_storage_disks(self, **kwargs):
        return (200, {}, {})

    def get_storage_disks_1(self, **kwargs):
        return (200, {}, {'1': {}})

    def put_storage_disks_1(self, **kwargs):
        return (200, {}, {'1': {}})

    def get_chassis(self, **kwargs):
        return (200, {}, {})

    def put_chassis_system_writeMem(self, **kwargs):
        return (200, {}, {})

    def get_chassis_fanTray(self, **kwargs):
        return (200, {}, {})

    def get_chassis_fanTray_1(self, **kwargs):
        return (200, {}, {})

    def get_interfaces(self, **kwargs):
        return (200, {}, {})

    def get_interfaces_1(self, **kwargs):
        return (200, {}, {})

    def put_interfaces_1_shutdown(self, **kwargs):
        return (200, {}, {})

    def put_interfaces_1_vlans_taggedVlans(self, **kwargs):
        return (200, {}, {})

    def put_interfaces_1_vlans_untaggedVlans(self, **kwargs):
        return (200, {}, {})

    def put_storage_pools_1_pool_name(self, **kwargs):
        return (200, {}, {})

    def delete_storage_pools_1_pool_name(self, **kwargs):
        return (200, {}, {})

    def put_storage_pools_1(self, **kwargs):
        return (200, {}, {})

    def get_chassis_powersupply(self, **kwargs):
        return (200, {}, {})

    def get_chassis_powersupply_1(self, **kwargs):
        return (200, {}, {})

    def get_chassis_scard(self, **kwargs):
        return (200, {}, {})

    def get_chassis_scard_1(self, **kwargs):
        return (200, {}, {})

    def put_chassis_scard_1_mgmtMode(self, **kwargs):
        return (200, {}, {})

    def get_chassis_smcard(self, **kwargs):
        return (200, {}, {})

    def get_chassis_smcard_1(self, **kwargs):
        return (200, {}, {})

    def get_chassis_systems(self, **kwargs):
        return (200, {}, {})

    def put_chassis_system_switchover(self, **kwargs):
        return (200, {}, {})

    def put_chassis_system_reload(self, **kwargs):
        return (200, {}, {})
