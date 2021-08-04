from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock, patch
from ansible_collections.sodalite.k8s.plugins.modules.pvc import validate, definition
from ansible_collections.sodalite.k8s.plugins.module_utils.common import CommonValidation

from copy import deepcopy

full_params = dict(
    name='foo',
    labels=dict(foo='bar', foo1='bar1'),
    annotations=dict(foo='bar', foo1='bar1'),
    access_modes=['ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany'],
    selector=dict(
        match_labels=dict(release='stable'),
        match_expressions=[dict(
            key='environment',
            operator='In',
            values=['dev']
        )]
    ),
    storage_request='4Gi',
    storage_limit='8Gi',
    volume_name='dev-volume',
    storage_class_name='dev-storage-class',
    volume_mode='Block'
)

full_def = {
    "apiVersion": "v1",
    "kind": "PersistentVolumeClaim",
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
    'spec': {
        'accessModes': ['ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany'],
        'selector': {
            'matchExpressions': [
                {
                    'key': 'environment',
                    'operator': 'In',
                    'values': ['dev']
                }
            ],
            'matchLabels': {
                'release': 'stable'
            }
        },
        'resources': {
            'requests': {
                'storage': '4Gi'
            },
            'limits': {
                'storage': '8Gi'
            }
        },
        'volumeName': 'dev-volume',
        'storageClassName': 'dev-storage-class',
        'volumeMode': 'Block'
    }
}

min_params = dict(
    name='foo',
    access_modes=['ReadWriteOnce'],
    storage_request='4Gi',
    volume_mode='Filesystem'
)
min_def = {
    "apiVersion": "v1",
    "kind": "PersistentVolumeClaim",
    "metadata": {
        "name": 'foo',
    },
    'spec': {
        'accessModes': ['ReadWriteOnce'],

        'resources': {
            'requests': {
                'storage': '4Gi'
            }
        },
        'volumeMode': 'Filesystem'
    }
}


class TestValid:

    @staticmethod
    def test_valid():
        module = MagicMock()

        validate(module, full_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_valid_min_params():
        # this test ensures validator does not fail on minimal params
        module = MagicMock()

        validate(module, min_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_validate_selector():
        # make sure Validate function actually calls CommonValidation.selector with proper args
        module = MagicMock()
        with patch.object(CommonValidation, 'selector', return_value=None) as mock_selector:

            validate(module, full_def)
            mock_selector.assert_called_once_with(module, full_def)

    @staticmethod
    def test_validate_metadata():
        # make sure Validate function actually calls CommonValidation.metadata with proper args
        module = MagicMock()
        with patch.object(CommonValidation, 'metadata', return_value=None) as mock_metadata:
            validate(module, full_def)
            mock_metadata.assert_called_once_with(module, full_def)

    @staticmethod
    def test_invalid_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['metadata']['name'] = '_foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_resource_limits():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['resources']['limits']['storage'] = 'foobar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]quantity' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_resource_requests():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['resources']['requests']['storage'] = 'foobar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]quantity' in fail_msg, fail_msg


class TestDefinition:

    @staticmethod
    def test_full_params():
        assert definition(full_params) == full_def, \
            print(f'full_def={full_def}, definition(full_params)={definition(full_params)}')

    @staticmethod
    def test_minimal_params():
        # required and default params

        assert definition(min_params) == min_def, \
            print(f'test_def={min_def}, definition(test_params)={definition(min_params)}')
