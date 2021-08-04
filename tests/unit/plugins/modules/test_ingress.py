from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock, patch, call
from ansible_collections.sodalite.k8s.plugins.modules.ingress import validate, definition
from ansible_collections.sodalite.k8s.plugins.module_utils.common import CommonValidation

from copy import deepcopy

full_params = dict(
    name='foo',
    labels=dict(foo='bar', foo1='bar1'),
    annotations=dict(foo='bar', foo1='bar1'),
    ingress_class_name='custom-ingress',
    default_backend_service=dict(
        name='default-service',
        port='8080',
    ),
    rules=[dict(
        host='https-foo.bar.com',
        paths=[dict(path='/app',
                    path_type='Prefix',
                    backend_service=dict(name='service1', port='app-port'))]
    )],
    tls=[dict(
        hosts=['https-foo.bar.com'],
        secret='secret-tls'
    )]
)

full_def = {
    "apiVersion": "networking.k8s.io/v1",
    "kind": "Ingress",
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
    "spec": {
        "defaultBackend": {
            "service": {
                "name": 'default-service',
                "port": {
                    'number': 8080
                }
            }
        },
        "ingressClassName": 'custom-ingress',
        "rules": [
            {
                'host': 'https-foo.bar.com',
                'http': {
                    'paths': [
                        {
                            'backend': {
                                "service": {
                                    "name": 'service1',
                                    "port": {
                                        'name': 'app-port',
                                    }
                                }
                            },
                            'path': '/app',
                            'pathType': 'Prefix'
                        }
                    ]
                }
            }
        ],
        'tls': [
            {
                'hosts': ['https-foo.bar.com'],
                'secretName': 'secret-tls'
            }
        ]
    }
}

min_params_1 = dict(
    name='foo',
    default_backend_service=dict(
        name='default-service',
        port='8080',
    )
)

min_params_2 = dict(
    name='foo',
    rules=[dict(
        host='https-foo.bar.com',
        paths=[dict(backend_service=dict(name='service1', port='app-port'))]
    )]
)

min_def_1 = {
    "apiVersion": "networking.k8s.io/v1",
    "kind": "Ingress",
    "metadata": {
        "name": 'foo',
    },
    "spec": {
        "defaultBackend": {
            "service": {
                "name": 'default-service',
                "port": {
                    'number': 8080
                }
            }
        }
    }
}

min_def_2 = {
    "apiVersion": "networking.k8s.io/v1",
    "kind": "Ingress",
    "metadata": {
        "name": 'foo',
    },
    "spec": {
        "rules": [
            {
                'host': 'https-foo.bar.com',
                'http': {
                    'paths': [
                        {
                            'backend': {
                                "service": {
                                    "name": 'service1',
                                    "port": {
                                        'name': 'app-port',
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        ]
    }
}


class TestDefinition:

    @staticmethod
    def test_full_params():
        assert definition(full_params) == full_def, \
            print(f'full_def={full_def}, '
                  f'definition(full_params)={definition(full_params)}')

    @staticmethod
    def test_minimal_params_1():
        # required and default params

        assert definition(min_params_1) == min_def_1, \
            print(f'test_def={min_def_1}, definition(test_params)={definition(min_params_1)}')

    @staticmethod
    def test_minimal_params_2():
        # required and default params

        assert definition(min_params_2) == min_def_2, \
            print(f'test_def={min_def_2}, definition(test_params)={definition(min_params_2)}')


class TestValid:

    @staticmethod
    def test_valid():
        module = MagicMock()

        validate(module, full_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_valid_min_def_1():
        module = MagicMock()

        validate(module, min_def_1)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_valid_min_def_2():
        module = MagicMock()

        validate(module, min_def_2)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_invalid_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['metadata']['name'] = '_foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_validate_metadata():
        # make sure Validate function actually calls CommonValidation.metadata with proper args
        module = MagicMock()
        with patch.object(CommonValidation, 'metadata', return_value=None) as mock_metadata:
            validate(module, full_def)
            mock_metadata.assert_called_once_with(module, full_def)

    @staticmethod
    def test_default_backend_and_paths_missing():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec'].pop('defaultBackend')
        test_def['spec'].pop('rules')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'one of (default_backend_service, rules)' in fail_msg, fail_msg

    @staticmethod
    def test_default_backend_invalid_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['defaultBackend']['service']['name'] = '8abc'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'default_backend_service.name' in fail_msg, fail_msg
        assert 'lowercase dns-1135 label name' in fail_msg, fail_msg

    @staticmethod
    def test_default_backend_invalid_port_number():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['defaultBackend']['service']['port']['number'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'default_backend_service.port' in fail_msg, fail_msg
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_default_backend_invalid_port_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['defaultBackend']['service']['port']['name'] = 'a--b'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'default_backend_service.port' in fail_msg, fail_msg
        assert 'IANA_SVC_NAME' in fail_msg, fail_msg

    @staticmethod
    def test_rules_invalid_host():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['rules'][0]['host'] = '*'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'rules[0].host' in fail_msg, fail_msg
        assert 'a dns-1123 subdomain' in fail_msg, fail_msg
        assert 'wildcard dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_empty_paths():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['rules'][0]['http']['paths'] = list()

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'rules[0].paths' in fail_msg, fail_msg
        assert 'at least one parameter' in fail_msg, fail_msg

    @staticmethod
    def test_backend_service_invalid_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] = '42foo'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'backend_service.name' in fail_msg, fail_msg
        assert 'a lowercase dns-1135 label name' in fail_msg, fail_msg

    @staticmethod
    def test_backend_service_invalid_port_number():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['rules'][0]['http']['paths'][0]['backend']['service']['port']['number'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'backend_service.port' in fail_msg, fail_msg
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_backend_service_invalid_port_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['rules'][0]['http']['paths'][0]['backend']['service']['port']['name'] = 'iana--svc--name'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'backend_service.port' in fail_msg, fail_msg
        assert 'IANA_SVC_NAME' in fail_msg, fail_msg

    @staticmethod
    def test_rules_invalid_path():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['rules'][0]['http']['paths'][0]['path'] = 'foo/bar/..'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'rules[0].paths[0].path' in fail_msg, fail_msg
        assert 'url path' in fail_msg, fail_msg
        assert 'rfc 3986' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_tls_secret_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['tls'][0]['secretName'] = '_my-secret'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'tls[0].secret' in fail_msg, fail_msg
        assert 'a lowercase dns-1123 subdomain' in fail_msg, fail_msg
