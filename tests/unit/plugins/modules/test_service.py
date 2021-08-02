from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest.mock import MagicMock, patch
from ansible_collections.sodalite.k8s.plugins.modules.service import validate, definition
from ansible_collections.sodalite.k8s.plugins.module_utils.common import CommonValidation

from copy import deepcopy

min_params = dict(
    name='foo',
    ports=[
        dict(
            port=8080,
            target_port='my-port',
            protocol='UDP',
            name='service-port',
            node_port=8081
        )
    ],
    type='ClusterIP',
    internal_traffic_policy='Cluster',
    publish_not_ready_addresses=False,
    session_affinity='None'
)
min_def = {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
        "name": 'foo',
    },
    'spec': {
        'ports': [
            {
                'port': 8080,
                'targetPort': 'my-port',
                'protocol': 'UDP',
                'name': 'service-port',
                'nodePort': 8081,
            }
        ],
        'type': 'ClusterIP',
        'internalTrafficPolicy': 'Cluster',
        'publishNotReadyAddresses': False,
        'sessionAffinity': 'None',
    }
}


class TestDefinition:
    # some params are mutually exclusive, this object is here just to make sure
    # params get on right place in Service def

    full_params = dict(
        name='foo',
        labels=dict(foo='bar', foo1='bar1'),
        annotations=dict(foo='bar', foo1='bar1'),
        access_modes=['ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany'],
        selector=dict(app='MyApp'),
        ports=[
            dict(
                port=8080,
                target_port='my-port',
                protocol='UDP',
                name='service-port',
                node_port=8081
            ),
            dict(
                port=8080,
                target_port='5432',
                protocol='TCP',
                name='service-port-2',
                node_port=8081
            )
        ],
        type='ExternalName',
        ip_families=['IPv4', 'IPv6'],
        ip_families_policy='PreferDualStack',
        # cluster_ip should be equal to cluster_ips[0] in valid definition
        cluster_ip='10.11.12.13',
        cluster_ips=['192.168.1.1', '2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
        external_ips=['192.168.1.2', '2001:0db8:85a3:0000:0000:8a2e:0370:7335'],
        load_balancer_ip='192.168.1.3',
        load_balancer_source_ranges=['192.168.1.3/24', '2001:db8:abcd:0012::0/64'],
        load_balancer_class='custom/load-balancer',
        external_name='my-service.foo.bar.com',
        external_traffic_policy='Local',
        internal_traffic_policy='Cluster',
        health_check_node_port=5000,
        publish_not_ready_addresses=True,
        session_affinity='ClientIP',
        session_affinity_timeout=60

    )

    full_def = {
        "apiVersion": "v1",
        "kind": "Service",
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
            'selector': {
                'app': 'MyApp'
            },
            'ports': [
                {
                    'port': 8080,
                    'targetPort': 'my-port',
                    'protocol': 'UDP',
                    'name': 'service-port',
                    'nodePort': 8081,
                },
                {
                    'port': 8080,
                    'targetPort': 5432,
                    'protocol': 'TCP',
                    'name': 'service-port-2',
                    'nodePort': 8081,
                }
            ],
            'type': 'ExternalName',
            'ipFamilies': ['IPv4', 'IPv6'],
            'ipFamilyPolicy': 'PreferDualStack',
            # clusterIP should be equal to clusterIPs[0] in valid definition
            'clusterIP': '10.11.12.13',
            'clusterIPs': ['192.168.1.1', '2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
            'externalIPs': ['192.168.1.2', '2001:0db8:85a3:0000:0000:8a2e:0370:7335'],
            'loadBalancerIP': '192.168.1.3',
            'loadBalancerSourceRanges': ['192.168.1.3/24', '2001:db8:abcd:0012::0/64'],
            'loadBalancerClass': 'custom/load-balancer',
            'externalName': 'my-service.foo.bar.com',
            'externalTrafficPolicy': 'Local',
            'internalTrafficPolicy': 'Cluster',
            'healthCheckNodePort': 5000,
            'publishNotReadyAddresses': True,
            'sessionAffinity': 'ClientIP',
            'sessionAffinityConfig': {
                'clientIP': {
                    'timeoutSeconds': 60
                }
            }
        }
    }

    @staticmethod
    def test_full_params():
        assert definition(TestDefinition.full_params) == TestDefinition.full_def, \
            print(f'TestDefinition.full_def={TestDefinition.full_def}, '
                  f'definition(TestDefinition.full_params)={definition(TestDefinition.full_params)}')

    @staticmethod
    def test_copy_cluster_ip():
        test_params = deepcopy(TestDefinition.full_params)
        test_params.pop('cluster_ip')
        test_def = deepcopy(TestDefinition.full_def)
        test_def['spec']['clusterIP'] = test_def['spec']['clusterIPs'][0]
        assert definition(test_params) == test_def, \
            print(f'test_def={test_def}, definition(test_params)={definition(test_params)}')

    @staticmethod
    def test_minimal_params():
        # required and default params

        assert definition(min_params) == min_def, \
            print(f'test_def={min_def}, definition(test_params)={definition(min_params)}')

# class TestValid:
#
#     @staticmethod
#     def test_valid():
#         module = MagicMock()
#
#         validate(module, full_def)
#         module.fail_json.assert_not_called()
#
#     @staticmethod
#     def test_valid_min_params():
#         # this test ensures validator does not fail on minimal params
#         module = MagicMock()
#
#         validate(module, min_def)
#         module.fail_json.assert_not_called()
#
#     @staticmethod
#     def test_validate_selector():
#         # make sure Validate function actually calls CommonValidation.selector with proper args
#         module = MagicMock()
#         with patch.object(CommonValidation, 'selector', return_value=None) as mock_selector:
#
#             validate(module, full_def)
#             mock_selector.assert_called_once_with(module, full_def)
#
#     @staticmethod
#     def test_validate_metadata():
#         # make sure Validate function actually calls CommonValidation.metadata with proper args
#         module = MagicMock()
#         with patch.object(CommonValidation, 'metadata', return_value=None) as mock_metadata:
#             validate(module, full_def)
#             mock_metadata.assert_called_once_with(module, full_def)
#
#     @staticmethod
#     def test_invalid_name():
#         module = MagicMock()
#         test_def = deepcopy(full_def)
#         test_def['metadata']['name'] = '_foo_bar'
#
#         validate(module, test_def)
#         module.fail_json.assert_called()
#         fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
#         assert 'lowercase dns-1123 subdomain' in fail_msg, fail_msg
#
#     @staticmethod
#     def test_invalid_resource_limits():
#         module = MagicMock()
#         test_def = deepcopy(full_def)
#         test_def['spec']['resources']['limits']['storage'] = 'foobar'
#
#         validate(module, test_def)
#         module.fail_json.assert_called()
#         fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
#         assert 'map[string]quantity' in fail_msg, fail_msg
#
#     @staticmethod
#     def test_invalid_resource_requests():
#         module = MagicMock()
#         test_def = deepcopy(full_def)
#         test_def['spec']['resources']['requests']['storage'] = 'foobar'
#
#         validate(module, test_def)
#         module.fail_json.assert_called()
#         fail_msg = module.fail_json.call_args.kwargs['msg'].lower()
#         assert 'map[string]quantity' in fail_msg, fail_msg
#
#
# class TestDefinition:
#
#     @staticmethod
#     def test_full_params():
#         assert definition(full_params) == full_def, \
#             print(f'full_def={full_def}, definition(full_params)={definition(full_params)}')
#
#     @staticmethod
#     def test_minimal_params():
#         # required and default params
#
#         assert definition(min_params) == min_def, \
#             print(f'test_def={min_def}, definition(test_params)={definition(min_params)}')
