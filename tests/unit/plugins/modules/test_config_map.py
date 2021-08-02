from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.modules.config_map import validate, definition

from copy import deepcopy

params = dict(
    name='foo',
    labels=dict(foo='bar', foo2='bar2'),
    annotations=dict(foo='bar', foo2='bar2'),
    immutable=True,
    data=dict(foo1='bar'),
    binary_data=dict(foo='eWVrX2Vtb3M='),
)

valid_def = {
    "apiVersion": "v1",
    "kind": "ConfigMap",
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
    },
    "immutable": True,
    "data": {
        'foo1': 'bar'
    },
    "binaryData": {
        'foo': 'eWVrX2Vtb3M='
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
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'lowercase' in fail_msg
        assert 'dns' in fail_msg
        assert '1123' in fail_msg
        assert 'subdomain' in fail_msg

    @staticmethod
    def test_invalid_data_key():
        module = MagicMock()
        test_def = deepcopy(valid_def)
        test_def['binaryData']['invalid&key'] = 'eWVrX2Vtb3M='

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'keys' in fail_msg
        assert 'in' in fail_msg
        assert 'binary_data' in fail_msg

    @staticmethod
    def test_keys_overlap():
        module = MagicMock()
        test_def = deepcopy(valid_def)
        test_def['data']['foo'] = 'bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'should not overlap' in fail_msg
        assert ' data ' in fail_msg
        assert 'binary_data' in fail_msg

    @staticmethod
    def test_invalid_string_data_key():
        module = MagicMock()
        test_def = deepcopy(valid_def)
        test_def['data']['invalid&key'] = 'foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'keys' in fail_msg
        assert 'in' in fail_msg
        assert 'data' in fail_msg

    @staticmethod
    def test_binary_data_string_byte_dict():
        module = MagicMock()
        test_def = deepcopy(valid_def)
        test_def['binaryData']['some_key'] = 'foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'map[string][]byte' in fail_msg


class TestDefinition:

    @staticmethod
    def test_full_params():
        test_params = deepcopy(params)
        assert definition(test_params) == valid_def, \
            print(f'valid_def={valid_def}, definition(test_params)={definition(test_params)}')

    @staticmethod
    def test_minimal_params():
        test_params = dict(name='foo', immutable=False)  # immutable is a default param and is added by ansible
        test_def = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": 'foo',
            },
            "immutable": False,
        }
        assert definition(test_params) == test_def, \
            print(f'test_def={test_def}, definition(test_params)={definition(test_params)}')
