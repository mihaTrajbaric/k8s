from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.modules.namespace import validate, definition

from copy import deepcopy

params = dict(
    name='foo',
    labels=dict(foo='bar', foo2='bar2'),
    annotations=dict(foo='bar', foo2='bar2'),
)

valid_def = {
    "apiVersion": "v1",
    "kind": "Namespace",
    "metadata": {
        "name": 'foo',
        "labels": {
            'foo': 'bar',
            'foo2': 'bar2'
        },
        "annotations": {
            'foo': 'bar',
            'foo2': 'bar2'
        }
    }
}


class TestValidate:

    @staticmethod
    def test_valid():
        module = MagicMock()
        test_def = deepcopy(valid_def)

        validate(module, test_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_invalid_name():
        module = MagicMock()
        test_def = deepcopy(valid_def)
        test_def['metadata']['name'] = '_foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'lowercase dns-1123 subdomain' in fail_msg

    @staticmethod
    def test_invalid_metadata():
        module = MagicMock()
        test_def = deepcopy(valid_def)
        test_def['metadata']['labels']['foo'] = 1

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]string' in fail_msg


class TestDefinition:

    @staticmethod
    def test_full_params():
        test_params = deepcopy(params)
        assert definition(test_params) == valid_def

    @staticmethod
    def test_minimal_params():
        test_params = deepcopy(params)
        test_def = deepcopy(valid_def)
        test_params.pop('labels')
        test_params.pop('annotations')
        test_def['metadata'].pop('labels')
        test_def['metadata'].pop('annotations')

        assert definition(test_params) == test_def
