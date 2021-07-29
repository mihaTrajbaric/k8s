from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.module_utils.common import CommonValidation

from copy import deepcopy


def test_metadata_success():
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
            },
            'name': 'foo'
        }
    }
    CommonValidation.metadata(module, k8s_def)
    module.fail_json.assert_not_called()


def test_metadata_fail1():
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
            },
            'name': 'foo'
        }
    }
    CommonValidation.metadata(module, k8s_def)
    module.fail_json.assert_called_once()
    assert 'annotations' in module.fail_json.call_args.kwargs['msg'].lower()


def test_metadata_fail2():
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
            },
            'name': 'foo'
        }
    }
    CommonValidation.metadata(module, k8s_def)
    module.fail_json.assert_called_once()
    assert 'labels' in module.fail_json.call_args.kwargs['msg'].lower()


selector_def = {
    "spec": {
        'selector': {
            'matchExpressions': [
                {
                    'key': 'app',
                    'operator': 'In',
                    'values': ['test', 'test2', 'test3']
                }
            ],
            'matchLabels': {
                "app": "test"
            }
        },
    }
}


def test_selector_wrong_operator():
    module = MagicMock()

    test_def = deepcopy(selector_def)
    test_def['spec']['selector']['matchExpressions'][0]['operator'] = 'foo'

    CommonValidation.selector(module, test_def)
    module.fail_json.assert_called()
    assert 'operator' in module.fail_json.call_args.kwargs['msg'].lower()


def test_selector_empty_values():
    module = MagicMock()

    test_def = deepcopy(selector_def)
    test_def['spec']['selector']['matchExpressions'][0]['values'] = []

    CommonValidation.selector(module, test_def)
    module.fail_json.assert_called()
    fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
    assert 'non-empty' in fail_msg
    assert 'values' in fail_msg


def test_selector_exists_and_not_empty_values():
    module = MagicMock()

    test_def = deepcopy(selector_def)
    test_def['spec']['selector']['matchExpressions'][0]['operator'] = 'Exists'

    CommonValidation.selector(module, test_def)
    module.fail_json.assert_called()
    fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
    assert 'empty' in fail_msg
    assert 'values' in fail_msg


def test_selector_match_labels_wrong_type():
    module = MagicMock()

    test_def = deepcopy(selector_def)
    test_def['spec']['selector']['matchLabels']['app'] = 1

    CommonValidation.selector(module, test_def)
    module.fail_json.assert_called()
    fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
    assert 'map[string]string' in fail_msg
