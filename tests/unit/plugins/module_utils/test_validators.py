from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators


def test_alnum_ext():
    assert Validators.alnum_ext('foo-bar')
    assert Validators.alnum_ext('foo_bar')
    assert Validators.alnum_ext('foo.bar')
    assert Validators.alnum_ext('FooBar')
    assert Validators.alnum_ext('Foo.Bar-foo_bar')
    assert not Validators.alnum_ext('#foo+bar')


def test_dns_subdomain():
    assert Validators.dns_subdomain('a' * 253)
    assert not Validators.dns_subdomain('a' * 254)
    assert not Validators.dns_subdomain("aA3Bd2s")
    assert not Validators.dns_subdomain("ab3d_a")
    assert not Validators.dns_subdomain("3abd2a")
    assert not Validators.dns_subdomain("abd2")
    assert Validators.dns_subdomain("foo-bar.foo-35-bar")


def test_dns_label():
    assert Validators.dns_label('a' * 63)
    assert not Validators.dns_label('a' * 64)
    assert not Validators.dns_label("aA3Bd2s")
    assert not Validators.dns_label("ab3d_a")
    assert not Validators.dns_label("ab3d.a")
    assert not Validators.dns_label("3abd2a")
    assert not Validators.dns_label("abd2")
    assert Validators.dns_label("foo-bar-foo-35-bar")


def test_string_string_dict():
    assert Validators.string_string_dict({
        'foo': 'bar',
        'foo2': 'bar2'
    })
    assert not Validators.string_string_dict({
        'foo': 1,
    })
    assert not Validators.string_string_dict({
        'foo': {
            'foo': 'bar'
        },
    })


def test_string_byte_dict():
    assert Validators.string_byte_dict({
        'foo': 'YmFy',  # bar in Base64
        'foo2': 'YmFyMg=='
    })
    assert not Validators.string_byte_dict({
        'foo': 1
    })
    assert not Validators.string_byte_dict({
        'foo': 'bar'
    })
    assert not Validators.string_byte_dict({
        'foo': {
            'foo': 'YmFy'
        },
    })


def test_base64():
    assert Validators.base64('cG9zdGdyZXM=')
    assert not Validators.base64('foo')


def quantity():
    # TODO implement when quantity validation is supported
    assert Validators.quantity('5Gi')


def string_quantity_dict():
    # TODO implement when quantity validation is supported
    assert Validators.string_quantity_dict({
        'foo': '5Gi'
    })
