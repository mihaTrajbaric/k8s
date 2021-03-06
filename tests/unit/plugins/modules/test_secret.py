from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.modules.secret import validate, definition

from copy import deepcopy

test_params = dict(
    name='foo',
    labels=dict(foo='bar', foo1='bar1'),
    annotations=dict(foo='bar', foo1='bar1'),
    immutable=True,
    string_data=dict(foo='bar'),
    data=dict(foo='eWVrX2Vtb3M='),
    type='Opaque'
)
full_def = {
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {
        "name": 'foo',
        "labels": {
            'foo': 'bar',
            'foo1': 'bar1'
        },
        "annotations": {
            'foo': 'bar',
            'foo1': 'bar1'
        }
    },
    "immutable": True,
    "type": 'Opaque',
    "stringData": {
        'foo': 'bar'
    },
    "data": {
        'foo': 'eWVrX2Vtb3M='
    }
}


class TestValidate:

    @staticmethod
    def test_valid():
        module = MagicMock()
        test_def = deepcopy(full_def)

        validate(module, test_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_invalid_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['metadata']['name'] = '_foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'lowercase' in fail_msg
        assert 'dns' in fail_msg
        assert '1123' in fail_msg
        assert 'subdomain' in fail_msg

    @staticmethod
    def test_invalid_data_key():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['data']['invalid&key'] = 'eWVrX2Vtb3M='

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'keys' in fail_msg
        assert 'in' in fail_msg
        assert 'data' in fail_msg

    @staticmethod
    def test_invalid_string_data_key():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['stringData']['invalid&key'] = 'foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'keys' in fail_msg
        assert 'in' in fail_msg
        assert 'string_data' in fail_msg

    @staticmethod
    def test_data_string_byte_dict():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['data']['some_key'] = 'foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string][]byte' in fail_msg

    @staticmethod
    def test_string_data_string_string_dict():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['stringData']['some_key'] = 1

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]string' in fail_msg


class TestDefinition:

    @staticmethod
    def test_minimal_params():
        test_params = dict(name='foo', immutable=False, type='Opaque')
        test_def = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": 'foo',
            },
            "immutable": False,
            'type': 'Opaque'
        }
        assert definition(test_params) == test_def, \
            print(f'test_def={test_def}, definition(test_params)={definition(test_params)}')

    @staticmethod
    def test_full_params():
        assert definition(test_params) == full_def, \
            print(f'full_def={full_def}, definition(test_params)={definition(test_params)}')
