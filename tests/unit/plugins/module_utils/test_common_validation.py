from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.module_utils.common import CommonValidation


def test_success():
    module = MagicMock()
    k8s_def = {
        'metadata': {
            'annotations': {
                'foo': 'bar',
                'foo2': 'bar2'
            },
            'labels': {
                'foo': 'bar',
                'foo2': 'bar2'
            }
        }
    }
    CommonValidation.metadata(module, k8s_def)
    module.fail_json.assert_not_called()


def test_fail1():
    module = MagicMock()
    k8s_def = {
        'metadata': {
            'annotations': {
                'foo': 1,
                'foo2': 'bar2'
            },
            'labels': {
                'foo': 'bar',
                'foo2': 'bar2'
            }
        }
    }
    CommonValidation.metadata(module, k8s_def)
    module.fail_json.assert_called_once()
    assert 'annotations' in module.fail_json.call_args.kwargs['msg'].lower()


def test_fail2():
    module = MagicMock()
    k8s_def = {
        'metadata': {
            'annotations': {
                'foo': 'bar',
                'foo2': 'bar2'
            },
            'labels': {
                'foo': 1,
                'foo2': 'bar2'
            }
        }
    }
    CommonValidation.metadata(module, k8s_def)
    module.fail_json.assert_called_once()
    assert 'labels' in module.fail_json.call_args.kwargs['msg'].lower()
