from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators


def test_alphanumeric():
    assert Validators.alphanumeric('foo-bar')
    assert Validators.alphanumeric('foo_bar')
    assert Validators.alphanumeric('foo.bar')
    assert Validators.alphanumeric('FooBar')
    assert Validators.alphanumeric('Foo.Bar-foo_bar')
    assert not Validators.alphanumeric('#foo+bar')


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
