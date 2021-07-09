from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.sodalite.k8s.plugins.module_utils.helper import clean_dict


def test_idempotency():
    test_dict = {
        'foo': 'bar',
        'nested_foo': {
            'foo': 'bar',
            'foo2': 'bar2'
        },
        'very_nested_foo': {
            'layer_one_foo': {
                'layer_two_foo': {
                    'foo': 'bar'
                },
                'layer_two_foo_2': 'bar'
            }
        }
    }
    assert clean_dict(test_dict) == test_dict


def test_remove_none():
    test = {
        'foo_empty1': None,
        'foo_empty2': {
            'foo': None,
            'foo2': {
                'foo': None
            }
        },
        'foo': 1,
        'foo2': {
            'foo_empty': {
                'foo': None
            },
            'foo': 'bar'
        }
    }
    result = {
        'foo': 1,
        'foo2': {
            'foo': 'bar'
        }
    }
    assert clean_dict(test) == result
