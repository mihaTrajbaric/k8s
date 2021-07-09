from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.sodalite.k8s.plugins.module_utils.common import Base64


def test_encode():
    assert Base64.encode('postgres') == 'cG9zdGdyZXM='


def test_decode():
    assert Base64.decode('cG9zdGdyZXM=') == 'postgres'


def test_validate():
    assert Base64.validate('cG9zdGdyZXM=')
    assert not Base64.validate('foo')
