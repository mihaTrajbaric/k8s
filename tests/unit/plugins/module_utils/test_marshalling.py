from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.sodalite.k8s.plugins.module_utils.common import Marshalling


def test_unmarshall_int_or_string():
    assert isinstance(Marshalling.unmarshall_int_or_string('8'), int)
    assert isinstance(Marshalling.unmarshall_int_or_string('asdf'), str)
    assert Marshalling.unmarshall_int_or_string(None) is None
