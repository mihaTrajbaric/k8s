from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock
from ansible_collections.sodalite.k8s.plugins.modules.storage_class import validate

from copy import deepcopy

storage_class_valid_def = {
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
                    'a': 'b',
                    'c': 'd'
                }
            ]
        }
    ],
    'mountOptions': 'rw',
    'parameters': {
        'a': 'b',
        'c': 'd'
    },
    'reclaimPolicy': 'Delete',
    'volumeBindingMode': 'Immediate'
}


def test_valid():
    module = MagicMock()
    test_def = deepcopy(storage_class_valid_def)

    validate(module, test_def)
    module.fail_json.assert_not_called()


def test_invalid_name():
    module = MagicMock()
    test_def = deepcopy(storage_class_valid_def)
    test_def['metadata']['name'] = '_foo_bar'

    validate(module, test_def)
    module.fail_json.assert_called()
    fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
    assert 'lowercase' in fail_msg
    assert 'dns' in fail_msg
    assert '1123' in fail_msg
    assert 'subdomain' in fail_msg


def test_invalid_params():
    module = MagicMock()
    test_def = deepcopy(storage_class_valid_def)
    test_def['parameters']['a'] = 1

    validate(module, test_def)
    module.fail_json.assert_called()
    fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
    assert 'map[string]string' in fail_msg
