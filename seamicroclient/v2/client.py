# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from seamicroclient import client
from seamicroclient.v2 import chassis
from seamicroclient.v2 import disks
from seamicroclient.v2 import fantrays
from seamicroclient.v2 import interfaces
from seamicroclient.v2 import pools
from seamicroclient.v2 import powersupplies
from seamicroclient.v2 import scards
from seamicroclient.v2 import servers
from seamicroclient.v2 import smcards
from seamicroclient.v2 import system
from seamicroclient.v2 import volumes


class Client(object):

    """
    Top-level object to access the Seamicro Chassis API.

    Create an instance with your creds::

        >>> client = Client(USERNAME, PASSWORD, AUTH_URL)

    Then call methods on its managers::

        >>> client.servers.list()
        ...
        >>> client.chassis.list()
        ...

    """

    def __init__(self, username, password, auth_url=None,
                 timeout=None, http_log_debug=False):
        self.servers = servers.ServerManager(self)
        self.pools = pools.PoolManager(self)
        self.volumes = volumes.VolumeManager(self)
        self.disks = disks.DiskManager(self)
        self.chassis = chassis.ChassisManager(self)
        self.fantrays = fantrays.FanTrayManager(self)
        self.interfaces = interfaces.InterfaceManager(self)
        self.powersupplies = powersupplies.PowerSupplyManager(self)
        self.scards = scards.ScardManager(self)
        self.smcards = smcards.SMCardManager(self)
        self.system = system.SystemManager(self)

        self.client = client.HTTPClient(username,
                                        password,
                                        auth_url=auth_url,
                                        timeout=timeout,
                                        http_log_debug=http_log_debug)

    def get_timings(self):
        return self.client.get_timings()

    def reset_timings(self):
        self.client.reset_timings()

    def authenticate(self):
        """
        Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
