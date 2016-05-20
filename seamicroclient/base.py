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
Base utilities to build API operation managers and objects on top of.
"""

import abc
import time

import six

from seamicroclient import exceptions
from seamicroclient.openstack.common import strutils
from seamicroclient import utils

# Python 3 does not have a basestring. In that case, we use str.
if 'basestring' not in dir(__builtins__):
    basestring = str


def getid(obj):
    """
    Abstracts the common pattern of allowing both an object or an object's ID
    as a parameter when dealing with relationships.
    """
    try:
        return obj.id
    except AttributeError:
        return obj


class Manager(utils.HookableMixin):

    """
    Managers interact with a particular type of API (servers, storage
    etc.) and provide CRUD operations for them.
    """
    resource_class = None

    def __init__(self, api):
        self.api = api

    def _list(self, url, body=None, filters=None):
        if body:
            _resp, body = self.api.client.post(url, body=body)
        else:
            _resp, body = self.api.client.get(url)

        obj_class = self.resource_class

        data = body
        output = []
        for k, v in data.items():
            if data[k]:
                if type(v) != dict:
                    output.append(obj_class(self, data, loaded=True))
                    break
                v.update({'id': k})
                output.append(obj_class(self, v, loaded=True))

        filtered_output = set()
        if filters is not None:
            for k, v in filters.items():
                for item in output:
                    if isinstance(v, basestring):
                        if v in getattr(item, k):
                            output.add(item)
                        else:
                            if item in output:
                                output.remove(item)
                    elif isinstance(v, int):
                        if v == getattr(item, k):
                            output.add(item)
                        else:
                            if item in output:
                                output.remove(item)
                    else:
                        continue
            return filtered_output
        return output

    def _get(self, id, url):
        _resp, body = self.api.client.get(url)
        body.update({'id': id})
        return self.resource_class(self, body)

    def _create(self, url, body, return_raw=False, **kwargs):
        self.run_hooks('modify_body_for_create', body, **kwargs)
        _resp, body = self.api.client.post(url, body=body)
        if isinstance(body, basestring):
            return body.partition('/')[-1]
        if return_raw:
            return body
        for k, v in body.items():
            v.update({'id': k})
            return self.resource_class(self, v)

    def _delete(self, url):
        _resp, _body = self.api.client.delete(url)

    def _update(self, url, body, **kwargs):
        self.run_hooks('modify_body_for_update', body, **kwargs)
        _resp, body = self.api.client.put(url, body=body)
        if body:
            if isinstance(body, basestring):
                return body.partition('/')[-1]

            if body == kwargs.get('action'):
                return
            for k, v in body.items():
                v.update({'id': k})
                return self.resource_class(self, v)


@six.add_metaclass(abc.ABCMeta)
class ManagerWithFind(Manager):

    """
    Like a `Manager`, but with additional `find()`/`findall()` methods.
    """

    @abc.abstractmethod
    def list(self):
        pass

    def find(self, **kwargs):
        """
        Find a single item with attributes matching ``**kwargs``.

        This isn't very efficient: it loads the entire list then filters on
        the Python side.
        """
        matches = self.findall(**kwargs)
        num_matches = len(matches)
        if num_matches == 0:
            msg = "No %s matching %s." % (self.resource_class.__name__, kwargs)
            raise exceptions.NotFound(404, msg)
        elif num_matches > 1:
            raise exceptions.NoUniqueMatch
        else:
            return matches[0]

    def findall(self, **kwargs):
        """
        Find all items with attributes matching ``**kwargs``.

        To find volume with size less than equal to 500 GB and id contains
        'ironic'

        kwargs = {'freeSize_le': 500, 'id_has': 'ironic', "UsedSize": 300}

        Operator:
        no operator required for "equal to" checks
        _le: less than equal to
        _ge: greater than equal to
        _has: contains string

        This isn't very efficient: it loads the entire list then filters on
        the Python side.
        """
        found = []
        searches = kwargs.items()

        listing = self.list()

        for obj in listing:
            try:
                for attr, value in searches:
                    if attr.endswith('_eq'):
                        if getattr(obj, attr) == value:
                            found.append(obj)
                    elif attr.endswith('_le'):
                        if getattr(obj, attr) <= value:
                            found.append(obj)
                    elif attr.endswith('_ge'):
                        if getattr(obj, attr) >= value:
                            found.append(obj)
                    elif attr.endswith('_has'):
                        if value in getattr(obj, attr):
                            found.append(obj)
                    else:
                        if getattr(obj, attr) == value:
                            found.append(obj)

            except AttributeError:
                continue

        return found


class Resource(object):

    """
    A resource represents a particular instance of an object (server, flavor,
    etc). This is pretty much just a bag for attributes.

    :param manager: Manager object
    :param info: dictionary representing resource attributes
    :param loaded: prevent lazy-loading if set to True
    """
    HUMAN_ID = False
    NAME_ATTR = 'id'

    def __init__(self, manager, info, loaded=False):
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    @property
    def human_id(self):
        """Subclasses may override this provide a pretty ID which can be used
        for bash completion.
        """
        if self.NAME_ATTR in self.__dict__ and self.HUMAN_ID:
            return strutils.to_slug(getattr(self, self.NAME_ATTR))
        return None

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def __getattr__(self, k):
        if k not in self.__dict__:
            # NOTE(rk): disallow lazy-loading if already loaded once
            if not self.is_loaded():
                self.get()
                return self.__getattr__(k)

            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and
                          k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self.set_loaded(True)
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.id)
        if new:
            self._add_details(new._info)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id == other.id
        return self._info == other._info

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val

    def refresh(self, sleep=None):
        if sleep:
            time.sleep(sleep)
        return self.manager.get(self.id)
