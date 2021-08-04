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


class TestValid:
    cluster_ip_max_def = {
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
                }
            ],
            'type': 'ClusterIP',
            'ipFamilies': ['IPv4', 'IPv6'],
            'ipFamilyPolicy': 'RequireDualStack',
            # clusterIP should be equal to clusterIPs[0] in valid definition
            'clusterIP': '192.168.1.1',
            'clusterIPs': ['192.168.1.1', '2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
            'externalIPs': ['192.168.1.2', '2001:0db8:85a3:0000:0000:8a2e:0370:7335'],
            'externalTrafficPolicy': 'Cluster',
            'internalTrafficPolicy': 'Local',
            'publishNotReadyAddresses': True,
            'sessionAffinity': 'ClientIP',
            'sessionAffinityConfig': {
                'clientIP': {
                    'timeoutSeconds': 600
                }
            }
        }
    }
    external_name_max_def = deepcopy(cluster_ip_max_def)
    external_name_max_def['spec'].pop('selector')
    external_name_max_def['spec'].pop('ipFamilies')
    external_name_max_def['spec'].pop('ipFamilyPolicy')
    external_name_max_def['spec'].pop('clusterIP')
    external_name_max_def['spec'].pop('clusterIPs')
    external_name_max_def['spec']['type'] = 'ExternalName'
    external_name_max_def['spec']['externalName'] = 'app.foo.bar.com'

    @staticmethod
    def test_cluster_ip_valid():
        module = MagicMock()

        validate(module, TestValid.cluster_ip_max_def)
        module.fail_json.assert_not_called()

    @staticmethod
    def test_validate_metadata():
        # make sure Validate function actually calls CommonValidation.metadata with proper args
        module = MagicMock()
        with patch.object(CommonValidation, 'metadata', return_value=None) as mock_metadata:
            validate(module, TestValid.cluster_ip_max_def)
            mock_metadata.assert_called_once_with(module, TestValid.cluster_ip_max_def)

    @staticmethod
    def test_invalid_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['metadata']['name'] = '_foo_bar'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'dns-1135 label name' in fail_msg, fail_msg

    @staticmethod
    def test_selector_with_external_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.external_name_max_def)
        test_def['spec']['selector'] = dict(app='a')
        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'selector' in fail_msg, fail_msg
        assert "not allowed with type='ExternalName'" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_selector():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['selector']['app'] = 1

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'map[string]string' in fail_msg, fail_msg

    @staticmethod
    def test_empty_ports():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec'].pop('ports')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'at least one element' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_ports_port():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'][0]['port'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_ports_target_port_number():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'][0]['targetPort'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_ports_target_port_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'][0]['targetPort'] = 'port--name'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'valid IANA_SVC_NAME' in fail_msg, fail_msg

    @staticmethod
    def test_port_name_not_unique():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'].append(test_def['spec']['ports'][0])

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'duplicate port name' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_port_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'][0]['name'] = '-port_name'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'dns-1123 label name' in fail_msg, fail_msg

    @staticmethod
    def test_multi_port_no_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'].append(test_def['spec']['ports'][0])
        test_def['spec']['ports'][1].pop('name')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg'].lower()
        assert 'name is not set' in fail_msg, fail_msg

    @staticmethod
    def test_invalid_ports_node_port():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)
        test_def['spec']['ports'][0]['nodePort'] = 808080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'valid port number' in fail_msg, fail_msg

    @staticmethod
    def test_ip_families_with_external_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.external_name_max_def)
        test_def['spec']['ipFamilies'] = ['IPv4', 'IPv6']
        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'ip_families' in fail_msg, fail_msg
        assert "not allowed with type='ExternalName'" in fail_msg, fail_msg

    @staticmethod
    def test_ip_family_policies_with_external_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.external_name_max_def)
        test_def['spec']['ipFamilyPolicy'] = 'RequireDualStack'
        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'ip_families_policy' in fail_msg, fail_msg
        assert "not allowed with type='ExternalName'" in fail_msg, fail_msg

    @staticmethod
    def test_more_than_2_ip_families():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        # ipFamilies already has two elements, one more should be enough
        test_def['spec']['ipFamilies'].append('IPv6')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'maximum of two entries' in fail_msg, fail_msg

    @staticmethod
    def test_repeat_same_ip_family():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        # ipFamilies already has two elements, one more should be enough
        test_def['spec']['ipFamilies'] = ['IPv6', 'IPv6']

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'more than once' in fail_msg, fail_msg

    @staticmethod
    def test_ip_families_and_single_stack():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        # ipFamilies already has two elements, one more should be enough
        test_def['spec']['ipFamilyPolicy'] = 'SingleStack'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "must be set to 'RequireDualStack' or 'PreferDualStack'" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ip_with_external_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.external_name_max_def)
        test_def['spec']['clusterIP'] = '192.168.1.1'
        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'cluster_ip' in fail_msg, fail_msg
        assert "not allowed with type='ExternalName'" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ips_with_external_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.external_name_max_def)
        test_def['spec']['clusterIPs'] = ['192.168.1.1', '2001:0db8:85a3:0000:0000:8a2e:0370:7334']
        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'cluster_ip' in fail_msg, fail_msg
        assert "not allowed with type='ExternalName'" in fail_msg, fail_msg

    @staticmethod
    def test_more_than_2_cluster_ips():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        # clusterIPs already has two elements, one more should be enough
        test_def['spec']['clusterIPs'].append('192.168.1.1')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "maximum of two entries" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ips_and_single_stack():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        # ipFamilies already has two elements, one more should be enough
        test_def['spec']['ipFamilyPolicy'] = 'SingleStack'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "must be set to 'RequireDualStack' or 'PreferDualStack'" in fail_msg, fail_msg
        assert "ip_families_policy" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ips_from_same_family():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        # ipFamilies already has two elements, one more should be enough
        test_def['spec']['clusterIPs'] = ['192.168.1.1', '192.168.1.2']

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'must be IPv4 and other IPv6' in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ips_ip_family_no_in_sync_ipv4():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['clusterIPs'] = ['2001:0db8:85a3:0000:0000:8a2e:0370:7334', '192.168.1.2']
        test_def['spec']['ipFamilies'] = ['IPv4']

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'a valid IPv4 address' in fail_msg, fail_msg
        assert "['IPv4']" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ips_ip_family_no_in_sync_ipv6():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['clusterIPs'] = ['2001:0db8:85a3:0000:0000:8a2e:0370:7334', '192.168.1.2']
        test_def['spec']['ipFamilies'] = ['IPv6']

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'a valid IPv6 address' in fail_msg, fail_msg
        assert "['IPv6']" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ips_not_valid_ips():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['clusterIPs'] = ['foo', 'bar']
        test_def['spec']['ipFamilies'] = ['IPv4', 'IPv6']

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'cluster_ips' in fail_msg, fail_msg
        assert 'valid IPv4 or IPv6 address' in fail_msg, fail_msg
        assert "['IPv4', 'IPv6']" in fail_msg, fail_msg

    @staticmethod
    def test_cluster_ip_not_valid_ip():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['clusterIP'] = 'foo'
        test_def['spec']['ipFamilies'] = ['IPv4', 'IPv6']

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'cluster_ip' in fail_msg, fail_msg
        assert 'valid IPv4 or IPv6 address' in fail_msg, fail_msg
        assert "['IPv4', 'IPv6']" in fail_msg, fail_msg

    @staticmethod
    def test_external_ips_not_valid():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['externalIPs'].append('foo')

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'external_ips' in fail_msg, fail_msg
        assert 'valid IPv4 or IPv6 address' in fail_msg, fail_msg

    @staticmethod
    def test_load_balancer_params_without_load_balancer():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['loadBalancerClass'] = 'custom/load-balancer'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "only valid with type='LoadBalancer'" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_load_balancer_ip():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['type'] = 'LoadBalancer'
        test_def['spec']['loadBalancerIP'] = '192.168.1.300'    # invalid IPv4 address

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "load_balancer_ip" in fail_msg, fail_msg
        assert "valid IPv4 or IPv6 address" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_load_balancer_source_ranges():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['type'] = 'LoadBalancer'
        test_def['spec']['loadBalancerSourceRanges'] = ['192.168.1.3/42']  # invalid IPv4 range

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "load_balancer_source_ranges" in fail_msg, fail_msg
        assert "IP range" in fail_msg, fail_msg

    @staticmethod
    def test_external_name_without_external_name_service_type():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['type'] = 'LoadBalancer'  # not ExternalName
        test_def['spec']['externalName'] = 'foo.com'

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "external_name" in fail_msg, fail_msg
        assert "only valid with type='ExternalName'" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_external_name():
        module = MagicMock()
        test_def = deepcopy(TestValid.external_name_max_def)
        test_def['spec']['externalName'] = "_foo-bar"
        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert 'external_name' in fail_msg, fail_msg
        assert "lowercase DNS-1123 subdomain" in fail_msg, fail_msg

    @staticmethod
    def test_health_check_node_port_without_load_balancer():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['type'] = 'ClusterIP'   # not LoadBalancer
        test_def['spec']['healthCheckNodePort'] = 8080

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "health_check_node_port" in fail_msg, fail_msg
        assert "type='LoadBalancer'" in fail_msg, fail_msg
        assert "external_traffic_policy='Local'" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_health_check_node_port():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['type'] = 'LoadBalancer'
        test_def['spec']['healthCheckNodePort'] = 808080    # invalid port

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "health_check_node_port" in fail_msg, fail_msg
        assert "valid port number" in fail_msg, fail_msg

    @staticmethod
    def test_session_affinity_timeout_without_session_affinity_client_ip():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['sessionAffinity'] = 'None'
        test_def['spec']['sessionAffinityConfig']['clientIP']['timeoutSeconds'] = 60

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "session_affinity_timeout" in fail_msg, fail_msg
        assert "session_affinity='ClientIP'" in fail_msg, fail_msg

    @staticmethod
    def test_invalid_session_affinity_timeout():
        module = MagicMock()
        test_def = deepcopy(TestValid.cluster_ip_max_def)

        test_def['spec']['sessionAffinity'] = 'ClientIP'
        test_def['spec']['sessionAffinityConfig']['clientIP']['timeoutSeconds'] = 864001

        validate(module, test_def)
        module.fail_json.assert_called()
        fail_msg = module.fail_json.call_args[1]['msg']
        assert "session_affinity_timeout" in fail_msg, fail_msg
        assert "0 < x <= 86400" in fail_msg, fail_msg

    @staticmethod
    def test_valid_min_params():
        # this test ensures validator does not fail on minimal params
        module = MagicMock()

        validate(module, min_def)
        module.fail_json.assert_not_called()
