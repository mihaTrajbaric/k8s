from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.modules.storage_class import validate, definition

from copy import deepcopy

full_params = dict(
    name='foo',
    labels=dict(foo='bar', foo1='bar1'),
    annotations=dict(foo='bar', foo1='bar1'),
    provisioner='k8s.io/minikube-hostpath',
    allow_volume_expansion=True,
    allowed_topologies=[dict(
        key='failure-domain.beta.kubernetes.io/zone',
        values=["us-central1-a", "us-central1-b"]
    )],
    mount_options='rw',
    parameters=dict(a='b', c='d'),
    reclaim_policy='Recycle',
    volume_binding_mode='WaitForFirstConsumer'
)

full_def = {
    "apiVersion": "storage.k8s.io/v1",
    "kind": "StorageClass",
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
    'provisioner': 'k8s.io/minikube-hostpath',
    'allowVolumeExpansion': True,
    'allowedTopologies': [
        {
            'matchLabelExpressions': [
                {
                    'key': 'failure-domain.beta.kubernetes.io/zone',
                    'values': [
                        "us-central1-a",
                        "us-central1-b"
                    ]

                }
            ]
        }
    ],
    'mountOptions': 'rw',
    'parameters': {
        'a': 'b',
        'c': 'd'
    },
    'reclaimPolicy': 'Recycle',
    'volumeBindingMode': 'WaitForFirstConsumer'
}

min_params = dict(
    name='foo',
    provisioner='k8s.io/minikube-hostpath',
    reclaim_policy='Delete',
    volume_binding_mode='Immediate'
)
min_def = {
    "apiVersion": "storage.k8s.io/v1",
    "kind": "StorageClass",
    "metadata": {
        "name": 'foo',
    },
    'provisioner': 'k8s.io/minikube-hostpath',
    'reclaimPolicy': 'Delete',
    'volumeBindingMode': 'Immediate'
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
    def test_invalid_metadata():
        # one test is sufficient, just to make sure
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['metadata']['labels']['foo'] = 1

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]string' in fail_msg

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
    def test_invalid_params():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['parameters']['a'] = 1

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]string' in fail_msg


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
