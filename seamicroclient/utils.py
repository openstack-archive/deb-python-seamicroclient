#
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

import os
import pkg_resources
import sys
import uuid

import six

from seamicroclient import exceptions
from seamicroclient.openstack.common import strutils


def env(*args, **kwargs):
    """
    returns the first environment variable set
    if none are non-empty, defaults to '' or keyword arg default
    """
    for arg in args:
        value = os.environ.get(arg, None)
        if value:
            return value
    return kwargs.get('default', '')


def find_resource(manager, name_or_id, **find_args):
    """Helper for the _find_* methods."""
    # first try to get entity as integer id
    try:
        return manager.get(int(name_or_id))
    except (TypeError, ValueError, exceptions.NotFound):
        pass

    # now try to get entity as uuid
    try:
        tmp_id = strutils.safe_encode(name_or_id)
        if six.PY3:
            tmp_id = tmp_id.decode()
        uuid.UUID(tmp_id)
        return manager.get(tmp_id)
    except (TypeError, ValueError, exceptions.NotFound):
        pass

    # for str id which is not uuid (for Flavor search currently)
    if getattr(manager, 'is_alphanum_id_allowed', False):
        try:
            return manager.get(name_or_id)
        except exceptions.NotFound:
            pass

    try:
        try:
            return manager.find(human_id=name_or_id, **find_args)
        except exceptions.NotFound:
            pass

        # finally try to find entity by name
        try:
            resource = getattr(manager, 'resource_class', None)
            name_attr = resource.NAME_ATTR if resource else 'name'
            kwargs = {name_attr: name_or_id}
            kwargs.update(find_args)
            return manager.find(**kwargs)
        except exceptions.NotFound:
            msg = "No %s with a name or ID of '%s' exists." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
    except exceptions.NoUniqueMatch:
        msg = ("Multiple %s matches found for '%s', use an ID to be more"
               " specific." % (manager.resource_class.__name__.lower(),
                               name_or_id))
        raise exceptions.CommandError(msg)


def _format_field_name(attr):
    """Format an object attribute in a human-friendly way."""
    # Split at ':' and leave the extension name as-is.
    parts = attr.rsplit(':', 1)
    name = parts[-1].replace('_', ' ')
    # Don't title() on mixed case
    if name.isupper() or name.islower():
        name = name.title()
    parts[-1] = name
    return ': '.join(parts)


def _make_field_formatter(attr, filters=None):
    """
    Given an object attribute, return a formatted field name and a
    formatter suitable for passing to print_list.

    Optionally pass a dict mapping attribute names to a function. The function
    will be passed the value of the attribute and should return the string to
    display.
    """
    filter_ = None
    if filters:
        filter_ = filters.get(attr)

    def get_field(obj):
        field = getattr(obj, attr, '')
        if field and filter_:
            field = filter_(field)
        return field

    name = _format_field_name(attr)
    formatter = get_field
    return name, formatter


class HookableMixin(object):

    """Mixin so classes can register and run hooks."""
    _hooks_map = {}

    @classmethod
    def add_hook(cls, hook_type, hook_func):
        if hook_type not in cls._hooks_map:
            cls._hooks_map[hook_type] = []

        cls._hooks_map[hook_type].append(hook_func)

    @classmethod
    def run_hooks(cls, hook_type, *args, **kwargs):
        hook_funcs = cls._hooks_map.get(hook_type) or []
        for hook_func in hook_funcs:
            hook_func(*args, **kwargs)


def safe_issubclass(*args):
    """Like issubclass, but will just return False if not a class."""

    try:
        if issubclass(*args):
            return True
    except TypeError:
        pass

    return False


def import_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    return getattr(sys.modules[mod_str], class_str)


def _load_entry_point(ep_name, name=None):
    """Try to load the entry point ep_name that matches name."""
    for ep in pkg_resources.iter_entry_points(ep_name, name=name):
        try:
            return ep.load()
        except (ImportError, pkg_resources.UnknownExtra, AttributeError):
            continue


def is_integer_like(val):
    """Returns validation of a value as an integer."""
    try:
        value = int(val)
        return True
    except (TypeError, ValueError, AttributeError):
        return False
