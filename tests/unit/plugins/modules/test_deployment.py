from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock, patch, call
from ansible_collections.sodalite.k8s.plugins.modules.deployment import validate, definition
from ansible_collections.sodalite.k8s.plugins.module_utils.common import CommonValidation

from copy import deepcopy

full_params = dict(
    name='foo',
    labels=dict(foo='bar', foo1='bar1'),
    annotations=dict(foo='bar', foo1='bar1'),
    selector=dict(
        match_labels=dict(release='stable'),
        match_expressions=[dict(
            key='environment',
            operator='In',
            values=['dev']
        )]
    ),
    containers=[dict(
        name='container-foo',
        image='test-image',
        image_pull_policy='Always',
        command=['python3', '-m test'],
        args=['foo', 'bar'],
        working_dir='/home/test',
        ports=[
            dict(
                name='first-port',
                container_port=8080,
                host_ip="77.43.66.2",
                host_port=5000,
                protocol='UDP'
            ),
            dict(
                name='second-port',
                container_port=8081,
                host_ip="77.43.66.3",
                host_port=5001,
                protocol='UDP'
            )
        ],
        env=[
            dict(
                name='FIRST_VAR',
                value='foo'
            ),
            dict(
                name='SECOND_VAR',
                config_map=dict(
                    name='db-config',
                    key='db-name',
                    optional=False
                )
            ),
            dict(
                name='THIRD_VAR',
                secret=dict(
                    name='db-secret-config',
                    key='db-pass',
                    optional=True
                )
            )
        ],
        env_from=[
            dict(
                prefix='DB_',
                config_map=dict(
                    name='db-config',
                    optional=False
                )
            ),
            dict(
                secret=dict(
                    name='db-secret-config',
                    optional=False
                )
            )
        ],
        volume_mounts=[
            dict(
                name='app-data',
                path='/home/test',
                propagation='HostToContainer',
                read_only=True,
                sub_path='foo/bar/'
            ),
            dict(
                name='app-data-2',
                path='/home/test2',
                propagation='Bidirectional',
                read_only=False,
                sub_path_expr='foo/bar/$(VAR_NAME)'
            )
        ],
        volume_devices=[
            dict(
                name='volume-device',
                path='/home/volume/device'
            )
        ],
        resource_limits=dict(
            cpu="1",
            memory='8Gi'
        ),
        resource_requests=dict(
            cpu="0.1",
            memory='4Gi'
        )
    )],
    image_pull_secrets=['my-secret', 'my-other-secret'],
    enable_service_links=False,
    volumes=[
        dict(
            name='app-data',
            config_map=dict(
                name='app-config',
                optional=False,
                default_mode=0o600,
                items=[
                    dict(
                        key='config-key',
                        path='/home/config/key.txt',
                        mode='0o644'
                    )
                ]
            ),
        ),
        dict(
            name='app-data-2',
            secret=dict(
                name='app-secret',
                optional=False,
                default_mode=0o600,
                items=[
                    dict(
                        key='secret-key',
                        path='/home/secret/key.txt',
                        mode='0o700'
                    )
                ]
            ),
        ),
        dict(
            name='volume-device',
            pvc=dict(
                claim_name='pvc-clain',
                read_only=True
            ),
        )
    ],
    replicas=3,
    min_ready_seconds=300,
    strategy=dict(
        type='RollingUpdate',
        max_surge='50%',
        max_unavailable='50%'
    ),
    revision_history_limit=7,
    progress_deadline_seconds=500,
    paused=False,
)

full_def = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
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
        "template": {
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
                'containers': [
                    {
                        'name': 'container-foo',
                        'image': 'test-image',
                        'imagePullPolicy': 'Always',
                        'command': ['python3', '-m test'],
                        'args': ['foo', 'bar'],
                        'workingDir': '/home/test',
                        'ports': [
                            {
                                'containerPort': 8080,
                                'hostIP': "77.43.66.2",
                                'hostPort': 5000,
                                'name': 'first-port',
                                'protocol': 'UDP',
                            },
                            {
                                'containerPort': 8081,
                                'hostIP': "77.43.66.3",
                                'hostPort': 5001,
                                'name': 'second-port',
                                'protocol': 'UDP',
                            }

                        ],
                        'env': [
                            {
                                'name': 'FIRST_VAR',
                                'value': 'foo'
                            },
                            {
                                'name': 'SECOND_VAR',
                                'valueFrom': {
                                    'configMapKeyRef': {
                                        'name': 'db-config',
                                        'key': 'db-name',
                                        'optional': False
                                    },
                                },
                            },
                            {
                                'name': 'THIRD_VAR',
                                'valueFrom': {
                                    'secretKeyRef': {
                                        'name': 'db-secret-config',
                                        'key': 'db-pass',
                                        'optional': True
                                    },
                                },
                            }

                        ],
                        'envFrom': [
                            {
                                'configMapRef': {
                                    'name': 'db-config',
                                    'optional': False
                                },
                                'prefix': 'DB_',
                            },
                            {
                                'secretRef': {
                                    'name': 'db-secret-config',
                                    'optional': False
                                },
                            }
                        ],
                        'volumeMounts': [
                            {
                                'mountPath': '/home/test',
                                'name': 'app-data',
                                'mountPropagation': 'HostToContainer',
                                'readOnly': True,
                                'subPath': 'foo/bar/',
                            },
                            {
                                'mountPath': '/home/test2',
                                'name': 'app-data-2',
                                'mountPropagation': 'Bidirectional',
                                'readOnly': False,
                                'subPathExpr': 'foo/bar/$(VAR_NAME)'
                            }

                        ],
                        'volumeDevices': [
                            {
                                'devicePath': '/home/volume/device',
                                'name': 'volume-device'
                            }
                        ],
                        'resources': {
                            'limits': {
                                'cpu': "1",
                                'memory': '8Gi'
                            },
                            'requests': {
                                'cpu': "0.1",
                                'memory': '4Gi'
                            }
                        }
                    }
                ],
                'imagePullSecrets': [
                    {"name": "my-secret"},
                    {"name": "my-other-secret"}
                ],
                'enableServiceLinks': False,
                'volumes': [
                    {
                        'name': 'app-data',
                        'configMap': {
                            'name': 'app-config',
                            'optional': False,
                            'defaultMode': 0o600,
                            'items': [
                                {
                                    'key': 'config-key',
                                    'path': '/home/config/key.txt',
                                    'mode': '0o644'
                                }
                            ],
                        }
                    },
                    {
                        'name': 'app-data-2',
                        'secret': {
                            'secretName': 'app-secret',
                            'optional': False,
                            'defaultMode': 0o600,
                            'items': [
                                {
                                    'key': 'secret-key',
                                    'path': '/home/secret/key.txt',
                                    'mode': '0o700'
                                }
                            ],
                        }
                    },
                    {
                        'name': 'volume-device',
                        'persistentVolumeClaim': {
                            'claimName': 'pvc-clain',
                            'readOnly': True
                        }
                    }
                ]
            }
        },
        'replicas': 3,
        'minReadySeconds': 300,
        'strategy': {
            'type': 'RollingUpdate',
            'rollingUpdate': {
                'maxSurge': '50%',
                'maxUnavailable': '50%',
            }
        },
        'revisionHistoryLimit': 7,
        'progressDeadlineSeconds': 500,
        'paused': False
    }

}

min_params = dict(
    name='foo',
    labels=dict(foo='bar', foo1='bar1'),
    selector=dict(
        match_labels=dict(release='stable'),
    ),
    containers=[dict(
        name='container-foo',
        image='test-image',
    )],
    enable_service_links=True,
    replicas=1,
    min_ready_seconds=0,
    revision_history_limit=10,
    progress_deadline_seconds=600,
    paused=False,
)

min_def = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": 'foo',
        "labels": {
            'foo': 'bar',
            'foo1': 'bar1'
        }
    },
    "spec": {
        'selector': {
            'matchLabels': {
                'release': 'stable'
            }
        },
        "template": {
            "metadata": {
                "name": 'foo',
                "labels": {
                    'foo': 'bar',
                    'foo1': 'bar1'
                },
            },
            'spec': {
                'containers': [
                    {
                        'name': 'container-foo',
                        'image': 'test-image',

                    }
                ],
                'enableServiceLinks': True,
            }
        },
        'replicas': 1,
        'minReadySeconds': 0,
        'revisionHistoryLimit': 10,
        'progressDeadlineSeconds': 600,
        'paused': False
    }

}


class TestDefinition:

    @staticmethod
    def test_full_params():
        assert definition(full_params) == full_def, \
            print(f'full_def={full_def}, '
                  f'definition(full_params)={definition(full_params)}')

    @staticmethod
    def test_minimal_params():
        # required and default params

        assert definition(min_params) == min_def, \
            print(f'test_def={min_def}, definition(test_params)={definition(min_params)}')


class TestValid:

    @staticmethod
    def test_valid():
        module = MagicMock()

        validate(module, full_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_valid_min_def():
        module = MagicMock()

        validate(module, min_def)
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
            assert mock_metadata.call_count == 2, mock_metadata.call_count
            assert mock_metadata.mock_calls == \
                   [call(module, full_def), call(module, full_def['spec']['template'])], \
                mock_metadata.mock_calls

    @staticmethod
    def test_validate_selector():
        # make sure Validate function actually calls CommonValidation.selector with proper args
        module = MagicMock()
        with patch.object(CommonValidation, 'selector', return_value=None) as mock_selector:
            validate(module, full_def)
            mock_selector.assert_called_once_with(module, full_def)

    @staticmethod
    def test_no_containers():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'] = None

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'at least one container' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_container_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['name'] = '_foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'lowercase dns-1123 label name' in fail_msg, fail_msg

    @staticmethod
    def test_missing_image_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0].pop('image')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'image is missing' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_port_container_port():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'container_port' in fail_msg, fail_msg
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_port_host_port():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['ports'][0]['hostPort'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'host_port' in fail_msg, fail_msg
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_port_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['ports'][0]['name'] = '_foo+bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'name' in fail_msg, fail_msg
        assert 'IANA_SVC_NAME' in fail_msg, fail_msg

    @staticmethod
    def test_duplicate_port_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['ports'][0]['name'] = 'name'
        test_def['spec']['template']['spec']['containers'][0]['ports'][1]['name'] = 'name'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'duplicate port name' in fail_msg, fail_msg
        assert 'unique name' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_env_var_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['env'][0]['name'] = 'MY--VAR'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'name' in fail_msg, fail_msg
        assert 'C_IDENTIFIER' in fail_msg, fail_msg

    @staticmethod
    def test_env_more_then_one_mode():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['env'].append(
            {
                'name': 'BROKEN_VAR',
                'value': 'foo',
                'valueFrom': {
                    'configMapKeyRef': {
                        'name': 'db-config',
                        'key': 'db-name'
                    },
                },
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'more then one value source' in fail_msg, fail_msg
        assert 'one of (value, config_map, secret)' in fail_msg, fail_msg

    @staticmethod
    def test_env_invalid_config_map_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['env'].append(
            {
                'name': 'BROKEN_VAR',
                'valueFrom': {
                    'configMapKeyRef': {
                        'name': '_db-config',
                        'key': 'db-name'
                    },
                },
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'config_map.name' in fail_msg, fail_msg
        assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_env_invalid_secret_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['env'].append(
            {
                'name': 'BROKEN_VAR',
                'valueFrom': {
                    'secretKeyRef': {
                        'name': '_db-secret',
                        'key': 'db-name'
                    },
                },
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'secret.name' in fail_msg, fail_msg
        assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_env_from_invalid_config_map_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['envFrom'].append(
            {
                'name': 'BROKEN_VAR',
                'configMapRef': {
                    'name': '_db-config',
                    'key': 'db-name'
                }
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'env_from' in fail_msg, fail_msg
        assert 'config_map.name' in fail_msg, fail_msg
        assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_env_from_more_then_one_source():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['envFrom'].append(
            {
                'name': 'BROKEN_VAR',
                'configMapRef': {
                    'name': 'db-config',
                    'key': 'db-name'
                },
                'secretRef': {
                    'name': 'db-secret',
                    'key': 'db-name'
                }
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'more then one value source' in fail_msg, fail_msg
        assert 'only one of (config_map, secret)' in fail_msg, fail_msg

    @staticmethod
    def test_env_from_invalid_secret_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['envFrom'].append(
            {
                'name': 'BROKEN_VAR',
                'secretRef': {
                    'name': '_db-broken',
                    'key': 'db-name'
                }
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'env_from' in fail_msg, fail_msg
        assert 'secret.name' in fail_msg, fail_msg
        assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg

    @staticmethod
    def test_env_from_invalid_prefix():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['envFrom'].append(
            {
                'name': 'BROKEN_VAR',
                'secretRef': {
                    'name': 'db-broken',
                    'key': 'db-name'
                },
                'prefix': 'a--b'
            })

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'env_from' in fail_msg, fail_msg
        assert 'prefix' in fail_msg, fail_msg
        assert 'C_IDENTIFIER' in fail_msg, fail_msg

    @staticmethod
    def test_volume_mount_without_volume():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['volumeMounts'][0]['name'] = 'foobar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'volume_mounts' in fail_msg, fail_msg
        assert 'name not found' in fail_msg, fail_msg

    @staticmethod
    def test_volume_mount_invalid_path():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = '/foo::bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'volume_mounts' in fail_msg, fail_msg
        assert 'path' in fail_msg, fail_msg
        assert "should not contain ':'" in fail_msg, fail_msg

    @staticmethod
    def test_volume_mount_sub_path_and_expr_exclusive():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['volumeMounts'][0]['subPath'] = 'some/path'
        test_def['spec']['template']['spec']['containers'][0]['volumeMounts'][0]['subPathExpr'] = 'some/path/$FOO'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'sub_path and sub_path_expr' in fail_msg, fail_msg
        assert 'mutually exclusive' in fail_msg, fail_msg

    @staticmethod
    def test_volume_devices_without_volume():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['volumeDevices'][0]['name'] = 'foobar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'volume_devices' in fail_msg, fail_msg
        assert 'name not found' in fail_msg, fail_msg

    @staticmethod
    def test_volume_device_volume_not_pvc():
        module = MagicMock()
        test_def = deepcopy(full_def)
        # app-data volume is config_map type
        test_def['spec']['template']['spec']['containers'][0]['volumeDevices'][0]['name'] = 'app-data'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'volume_devices' in fail_msg, fail_msg
        assert 'persistentVolumeClaim' in fail_msg, fail_msg

    @staticmethod
    def test_volume_device_invalid_path():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['volumeDevices'][0]['devicePath'] = '/foo::bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'volume_devices' in fail_msg, fail_msg
        assert 'path' in fail_msg, fail_msg
        assert "should not contain ':'" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_resource_limits_cpu():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'] = '1FooBarPerHour'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'resource_limits.cpu' in fail_msg, fail_msg
        assert "Quantities" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_resource_limits_cpu():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = '1FooBar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'resource_limits.memory' in fail_msg, fail_msg
        assert "Quantities" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_resource_requests_cpu():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu'] = '1FooBarPerHour'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'resource_requests.cpu' in fail_msg, fail_msg
        assert "Quantities" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_resource_requests_cpu():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['containers'][0]['resources']['requests']['memory'] = '1FooBar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg']
        assert 'resource_requests.memory' in fail_msg, fail_msg
        assert "Quantities" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_volume_name():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['volumes'][0]['name'] = '_volume_name'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'volumes' in fail_msg, fail_msg
        assert 'name' in fail_msg, fail_msg
        assert "lowercase dns-1123 label name" in fail_msg, fail_msg

    @staticmethod
    def test_more_then_one_volume_source():
        module = MagicMock()
        test_def = deepcopy(full_def)
        test_def['spec']['template']['spec']['volumes'].append(
            {
                'name': 'app-data',
                'configMap': {
                    'name': 'app-config',
                },
                'persistentVolumeClaim': {
                    'claimName': 'pvc-clain',
                    'readOnly': True
                }
            }
        )

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
        assert 'more then one volume source' in fail_msg, fail_msg
        assert 'one of (pvc, config_map, secret)' in fail_msg, fail_msg
