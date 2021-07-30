#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: service

short_description: Creates k8s Service

version_added: "1.0.0"

description: Creates k8s Service which is a named abstraction of software service (for example, mysql). It consists of
             local port (for example 3306) that the proxy listens on, and the selector that determines which pods will
             answer requests sent through the proxy.

extends_documentation_fragment:
    - sodalite.k8s.common_update_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    selector:
        description:
        - Route service traffic to pods with label keys and values matching this selector.
        - If empty or not present, the service is assumed to have an external process managing its
          endpoints, which Kubernetes will not modify.
        - Only applies to types I(ClusterIP), I(NodePort), and I(LoadBalancer).
        - Ignored if I(type=ExternalName).
        type: dict
    ports:
        description:
        - The list of ports that are exposed by this service.
        type: list
        elements: dict
        suboptions:
            port:
                description:
                - The port that will be exposed by this service.
                type: int
                required: true
            target_port:
                description:
                - Number or name of the port to access on the pods targeted by the service.
                - Number must be a valid port number (0 < x < 65536).
                - Name must be an IANA_SVC_NAME.
                - If this is a string, it will be looked up as a named port in the target Pod's container ports.
                - If this is not specified, the value of the I(port) field is used (an identity map).
                - This field is ignored for services with I(cluster_ip=None), and should be omitted or set
                  equal to the 'port' field.
                type: str
            protocol:
                description:
                - The IP protocol for this port.
                type: str
                default: TCP
                choices: [ UDP, TCP, SCTP ]
            name:
                description:
                - The name of this port within the service.
                - This must be a DNS_LABEL.
                - All ports within a Service must have unique names.
                - When considering the endpoints for a Service, this must match the I(name) field in the EndpointPort.
                - Required, if this service has more then one port.
                type: str
            node_port:
                description:
                - The port on each node on which this service is exposed.
                - Can be used with I(type=NodePort) or I(type=LoadBalancer).
                - Usually assigned by the system.
                - If a value is specified, in-range, and not in use it will be used, otherwise the operation will fail.
                - If not specified, a port will be allocated if this Service requires one.
                - If this field is specified when creating a Service which does not need it, creation will fail.
                - This field will be wiped when updating a Service to no longer need it (e.g. changing type from
                  NodePort to ClusterIP).
                type: int
    type:
        description:
        - Determines how the Service is exposed.
        - I(type==ClusterIP) exposes the Service on a cluster-internal IP. Choosing this value makes the Service only
          reachable from within the cluster. If I(cluster_ip=None), no virtual IP is allocated and the endpoints are
          published as a set of endpoints rather than a virtual IP.
        - I(type=NodePort) exposes the Service on each Node's IP at a static port (the NodePort). A ClusterIP Service,
          to which the NodePort Service routes, is automatically created. NodePort Service can be accessed from outside
          the cluster by requesting <NodeIP>:<NodePort>.
        - I(type=LoadBalancer) exposes the Service externally using a cloud provider's load balancer. NodePort and
          ClusterIP Services, to which the external load balancer routes, are automatically created. It routes to the
          same endpoints as the clusterIP.
        - I(type=ExternalName) maps the Service to the contents of the I(external_name) field
          (e.g. foo.bar.example.com), by returning a CNAME record with its value. No proxying of any kind is set up.
        type: str
        default: ClusterIP
        choices: [ ExternalName, ClusterIP, NodePort, LoadBalancer ]

    ip_families:
        description:
        - A list of IP families assigned to this service, and is gated by the "IPv6DualStack" feature gate.
        - This field is usually assigned automatically based on cluster configuration and the ipFamilyPolicy field.
        - If this field is specified manually, the requested family is available in the cluster, and ipFamilyPolicy
          allows it, it will be used; otherwise creation of the service will fail.
        - This field is conditionally mutable, it allows for adding or removing a secondary IP family, but it does not
          allow changing the primary IP family of the Service.
        - Cannot be used with I(type=ExternalName) and will be wiped when updating a Service to this type.
        - Does apply to "headless" services.
        - This field may hold a maximum of two entries (dual-stack families, in either order).
        - These families must correspond to the values in the I(cluster_ips) field, if specified.
        type: list
        elements: str
        choices: [ IPv4, IPv6 ]
    ip_families_policy:
        description:
        - Represents the dual-stack-ness requested or required by this Service, and is gated by the "IPv6DualStack"
          feature gate.
        - I(ip_families_policy=SingleStack) will enable a single IP family.
        - I(ip_families_policy=PreferDualStack) will enable two IP families on dual-stack configured clusters and a
          single IP family on single-stack clusters.
        - I(ip_families_policy=RequireDualStack) will enable two IP families on dual-stack configured clusters and fail
          on single-stack clusters.
        - The I(ip_families) and I(cluster_ips) fields depend on the value of this field.
        - This field cannot be used with I(type=ExternalName) and will be wiped when updating to a service of that type.
        type: str
        choices: [ SingleStack, PreferDualStack, RequireDualStack ]
    cluster_ip:
        description:
        - The IP address for the service.
        - It is usually assigned automatically.
        - If I(cluster_ip) address is in-range (as per system configuration), and is not in use, it will be
          allocated to the service; otherwise creation of the service will fail.
        - Valid values are "None", empty string (""), or a valid IP address.
        - Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint
          connections are preferred and proxying is not required.
        - Only applies to types ClusterIP, NodePort, and LoadBalancer.
        - If this field is specified when creating a Service of I(type=ExternalName), creation will fail.
        - This field may not be changed through updates unless the type field is also being changed to or from
          I(type=ExternalName) (ExternalName requires this field to be blank, otherwise it is optional)
        - This field will be wiped when updating a Service to type ExternalName.
        - Mutually exclusive with I(cluster_ips)
        type: str
    cluster_ips:
        description:
        - A list of IP addresses assigned to this service.
        - Every IP address must follow the same guidelines, as I(cluster_ip).
        - Cluster_ips[0] will be automatically added to clusterIP field in k8s definition.
        - Unless the "IPv6DualStack" feature gate is enabled, this field is limited to one value, otherwise, it may
          hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of
          the I(ip_families) field.
        - Mutually exclusive with I(cluster_ip)
        type: list
        elements: str
    external_ips:
        description:
        - A list of IP addresses for which nodes in the cluster will also accept traffic for this service.
        - These IPs are not managed by Kubernetes, the user is responsible for ensuring that traffic arrives at a node
          with this IP.
        - A common example is external load-balancers that are not part of the Kubernetes system.
        type: list
        elements: str
    load_balancer_ip:
        description:
        - Can be used only with I(type=LoadBalancer).
        - LoadBalancer will get created with the IP specified in this field.
        - This feature depends on whether the underlying cloud-provider supports specifying the loadBalancerIP when a
          load balancer is created.
        - It will be ignored if the cloud-provider does not support the feature.
        type: str
    load_balancer_source_ranges:
        description:
        - Can be used only with I(type=LoadBalancer).
        - Traffic through the cloud-provider load-balancer will be restricted to the specified client IPs.
        - Elements must be valid CIDR blocks (IPv4 or IPv6)
        - This field will be ignored if the cloud-provider does not support the feature.
        type: list
        elements: str
    load_balancer_class:
        description:
        - Can be used only with I(type=LoadBalancer).
        - The class of the load balancer implementation this Service belongs to.
        - If not set, the default load balancer implementation is used, today this is typically done through the cloud
          provider integration, but should apply for any default implementation.
        - If set, it is assumed that a load balancer implementation is watching for Services with a matching class.
        - Any default load balancer implementation (e.g. cloud providers) should ignore Services that set this field.
        - Once set, it can not be changed.
        - This field will be wiped when a service is updated to a non 'LoadBalancer' type.
        type: str
    external_name:
        description:
        - The external reference that discovery mechanisms will return as an alias for this service (e.g. a DNS
          CNAME record). No proxying will be involved.
        - Must be a lowercase RFC-1123 hostname.
        type: str
    external_traffic_policy:
        description:
        - Denotes if this Service desires to route external traffic to node-local or cluster-wide endpoints.
        - I(external_traffic_policy=Local) preserves the client source IP and avoids a second hop for LoadBalancer and
          Nodeport type services, but risks potentially imbalanced traffic spreading.
        - I(external_traffic_policy=Cluster) obscures the client source IP and may cause a second hop to another node,
          but should have good overall load-spreading.
        type: str
        choices: [ Local, Cluster ]
    internal_traffic_policy:
        description:
        - Specifies if the cluster internal traffic should be routed to all endpoints or node-local endpoints only.
        - I(internal_traffic_policy=Cluster) routes internal traffic to a Service to all endpoints.
        - I(internal_traffic_policy=Local) routes traffic to node-local endpoints only, traffic is dropped if no
          node-local endpoints are ready.
        type: str
        choices: [ Local, Cluster ]
        default: Cluster
    health_check_node_port:
        description:
        - Specifies the healthcheck nodePort for the service.
        - External systems (e.g. load-balancers) can use this port to determine if a given node holds endpoints for
          this service or not.
        - This only applies when I(type=LoadBalancer) and I(external_traffic_policy=Local).
        - If a value is specified, is in-range, and is not in use, it will be used.
        - If not specified, a value will be automatically allocated.
        - If this field is specified when creating a Service which does not need it, creation will fail.
        - This field will be wiped when updating a Service to no longer need it (e.g. changing type).
        type: int
    publish_not_ready_addresses:
        description:
        - I(publish_not_ready_addresses=true) indicates that any agent which deals with endpoints for this Service
          should disregard any indications of ready/not-ready.
        - The Kubernetes controllers that generate Endpoints and EndpointSlice resources for Services interpret this to
          mean that all endpoints are considered "ready" even if the Pods themselves are not.
        - Agents which consume only Kubernetes generated endpoints through the Endpoints or EndpointSlice resources can
          safely assume this behavior.
        type: bool
        default: false
    session_affinity:
        description:
        - Enable client IP based session affinity.
        - If I(session_affinity=ClientIP), connections from a particular client are passed to the same Pod each time.
        type: str
        default: None
        choices: [ ClientIP, None ]
    session_affinity_timeout:
        description:
        - The maximum session sticky time in seconds.
        - Can be used only with I(session_affinity=ClientIP).
        - The value must be 0 < x <= 86400 (1 day).
        type: int
        default: 10800

seealso:
- name: K8s Service documentation
  description: Complete service documentation on kubernetes website
  link: https://kubernetes.io/docs/concepts/services-networking/service/

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''

EXAMPLES = r'''
- name: Create simple Service
  sodalite.k8s.service:
    name: service-cluster-ip
    state: present
    ports:
    - name: my-port
      port: 8080

- name: Type NodePort with ip_families defined
  sodalite.k8s.service:
    name: service-test
    state: present
    type: NodePort
    ports:
    - name: my-port
      port: 8080
    ip_families:
    - IPv4
    ip_families_policy: SingleStack

- name: Specify ClusterIP
  sodalite.k8s.service:
    name: service-cluster-ip
    state: present
    ports:
    - name: my-port
      port: 8080
      target_port: xopera-port
      node_port: 30001
      protocol: TCP
    cluster_ip: 10.96.0.43

- name: Request IPv4/IPv6 dual stack
  sodalite.k8s.service:
    name: service-dual-stack
    state: present
    ports:
    - name: my-port
      port: 8080
    ip_families:
    - IPv4
    - IPv6
    ip_families_policy: RequireDualStack

- name: External IPs
  sodalite.k8s.service:
    name: service-external-ips
    state: present
    ports:
    - name: my-port
      port: 8080
    external_ips:
      - 77.54.34.1
      - 77.54.23.6

- name: External load balancer
  sodalite.k8s.service:
    name: service-load-balancer
    state: present
    type: LoadBalancer
    ports:
    - name: my-port
      port: 8080
    ip_families: ['IPv4', 'IPv6']
    ip_families_policy: RequireDualStack
    cluster_ips:
      - 10.96.1.1
      - 2001:db8:3333:4444:5555:6666:7777:8888
    load_balancer_ip: 77.230.145.14
    load_balancer_source_ranges:
      - 2001:db8:abcd:0012::0/64
      - 77.103.1.1/24
    load_balancer_class: internal-vip

- name: External name
  sodalite.k8s.service:
    name: service-external-name
    state: present
    type: ExternalName
    ports:
    - name: my-port
      port: 8080
    external_name: app.domain.com

- name: Policies and health_check
  sodalite.k8s.service:
    name: service-policies
    state: present
    type: LoadBalancer
    ports:
    - name: my-port
      port: 8080
    external_traffic_policy: Local
    internal_traffic_policy: Cluster
    health_check_node_port: 30000

- name: Disregard readiness of service
  sodalite.k8s.service:
    name: service-ready-irrelevant
    state: present
    ports:
    - name: my-port
      port: 8080
    publish_not_ready_addresses: yes

- name: Route client's requests to the same pod for 1 hour
  sodalite.k8s.service:
    name: service-session-affinity
    state: present
    ports:
    - name: my-port
      port: 8080
    session_affinity: ClientIP
    session_affinity_timeout: 60

- name: Remove Service
  sodalite.k8s.service:
    name: service-test
    state: absent
'''

RETURN = r'''
result:
  description:
  - The created, patched, or otherwise present object. Will be empty in the case of a deletion.
  returned: success
  type: complex
  contains:
     api_version:
       description: The versioned schema of this representation of an object.
       returned: success
       type: str
     kind:
       description: Represents the REST resource this object represents.
       returned: success
       type: str
     metadata:
       description: Standard object metadata. Includes name, namespace, annotations, labels, etc.
       returned: success
       type: dict
     spec:
       description: Specific attributes of the object.
       returned: success
       type: dict
     status:
       description: Current status details for the object.
       returned: success
       type: dict
     duration:
       description: elapsed time of task in seconds
       returned: when C(wait) is true
       type: int
       sample: 48
     error:
       description: error while trying to create/delete the object.
       returned: error
       type: dict
'''

from ansible_collections.sodalite.k8s.plugins.module_utils.ansiblemodule import AnsibleModule
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import (update_arg_spec,
                                                                               UPDATE_MUTUALLY_EXCLUSIVE)
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators, CommonValidation, Marshalling
from ansible_collections.sodalite.k8s.plugins.module_utils.helper import clean_dict

from copy import deepcopy


def definition(params):

    body = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        'spec': {
            'selector': params.get('selector'),
            'ports': [
                {
                    'port': port_obj.get('port'),
                    'targetPort': Marshalling.unmarshall_int_or_string(port_obj.get('target_port')),
                    'protocol': port_obj.get('protocol'),
                    'name': port_obj.get('name'),
                    'nodePort': port_obj.get('node_port'),
                }
                for port_obj in params.get('ports') or list()
            ],
            'type': params.get('type'),
            'ipFamilies': params.get('ip_families'),
            'ipFamilyPolicy': params.get('ip_families_policy'),
            'clusterIP': params.get('cluster_ip')
            or (params.get('cluster_ips')[0] if params.get('cluster_ips') else None),  # adds clusterIP[0] to clusterIP
            'clusterIPs': params.get('cluster_ips'),
            'externalIPs': params.get('external_ips'),
            'loadBalancerIP': params.get('load_balancer_ip'),
            'loadBalancerSourceRanges': params.get('load_balancer_source_ranges'),
            'loadBalancerClass': params.get('load_balancer_class'),
            'externalName': params.get('external_name'),
            'externalTrafficPolicy': params.get('external_traffic_policy'),
            'internalTrafficPolicy': params.get('internal_traffic_policy'),
            'healthCheckNodePort': params.get('health_check_node_port'),
            'publishNotReadyAddresses': params.get('publish_not_ready_addresses'),
            'sessionAffinity': params.get('session_affinity'),
            'sessionAffinityConfig': {
                'clientIP': {
                    'timeoutSeconds': params.get('session_affinity_timeout')
                }
            }
        }
    }
    return clean_dict(body)


def validate(module, k8s_definition):
    CommonValidation.metadata(module, k8s_definition)
    # for some reason, name should be a RFC 1035 Label Names
    if not Validators.dns_label_1035(k8s_definition['metadata']['name']):
        module.fail_json(msg=f"name {Validators.dns_label_1035_msg}")

    service_type = k8s_definition.get('spec').get('type')

    selector = k8s_definition.get('spec').get('selector')

    if selector:
        if service_type == 'ExternalName':
            module.fail_json(msg='selector is not allowed with type=ExternalName')
        if not Validators.string_string_dict(selector):
            module.fail_json(msg="selector should be map[string]string")

    # validate spec
    spec = k8s_definition['spec']

    # validate unique port names
    port_names = list()

    if len(spec.get('ports') or list()) < 1:
        module.fail_json(msg="ports must have at least one element")

    for i, port_obj in enumerate(spec.get('ports')):

        if not Validators.port(port_obj.get('port')):
            module.fail_json(msg=f"ports[{i}].port {Validators.port_msg}")

        target_port = port_obj.get('targetPort')
        if isinstance(target_port, int) and not Validators.port(target_port):
            module.fail_json(msg=f"ports[{i}].target_port is a number and {Validators.port_msg}")
        if isinstance(target_port, str) and not Validators.iana_svc_name(target_port):
            module.fail_json(msg=f"ports[{i}].target_port is a name and {Validators.iana_svc_name_msg}")

        port_name = port_obj.get('name')
        if port_name in port_names:
            module.fail_json(msg=f"Duplicate port name found (ports[{i}].name). "
                                 f"Each named port in a service must have a unique name")
        if port_name:
            port_names.append(port_name)
        if not Validators.dns_label(port_name):
            module.fail_json(msg=f"ports[{i}].name {Validators.dns_label_msg}")
        if len(spec.get('ports')) > 1 and port_name is None:
            module.fail_json(msg=f"ports[{i}].name is not set, but should be, since service has more then one port")

        if not Validators.port(port_obj.get('nodePort')):
            module.fail_json(msg=f"ports[{i}].node_port {Validators.port_msg}")

    ip_families = spec.get('ipFamilies') or list()
    ip_families_policy = spec.get('ipFamilyPolicy')

    if ip_families:
        if service_type == 'ExternalName':
            module.fail_json(msg='ip_families is not allowed with type=ExternalName')
        if len(ip_families) > 2:
            module.fail_json(msg='ip_families field may hold a maximum of two entries '
                                 '(dual-stack families, in either order)')
        if len(ip_families) == 2 and ip_families[0] == ip_families[1]:
            module.fail_json(msg='The same IP Family cannot be specified more then once')

        if len(ip_families) == 2 and ip_families_policy == 'SingleStack':
            module.fail_json(msg="ip_families_policy must be set to 'RequireDualStack' or 'PreferDualStack'"
                                 " when multiple ip_families are specified")

    # first verify cluster_ips; if cluster_ip had not been defined, it could be just copied from cluster_ips[0].
    # Validating cluster_ips first will make user get the right error message (with reference to cluster_ips[0],
    # not cluster_ip)

    cluster_ip = spec.get('clusterIP')
    cluster_ips = spec.get('clusterIPs') or []
    if service_type == 'ExternalName' and (cluster_ip or cluster_ips):
        module.fail_json(msg='cluster_ip and cluster_ips are not allowed with type=ExternalName')

    if cluster_ips:
        if len(cluster_ips) > 2:
            module.fail_json(msg='cluster_ips field may hold a maximum of two entries '
                                 '(dual-stack IPs, in either order. First IP will also be copied to ClusterIP field)')
        if len(cluster_ips) == 2:
            if ip_families_policy == 'SingleStack':
                module.fail_json(msg="ip_families_policy must be set to 'RequireDualStack' or 'PreferDualStack'"
                                     " when multiple cluster_ips are specified")

            # check if one is IPv4 and other IPv6
            if Validators.ipv4_address(cluster_ips[0]) and Validators.ipv4_address(cluster_ips[1]) or \
                    Validators.ipv6_address(cluster_ips[0]) and Validators.ipv6_address(cluster_ips[1]):
                module.fail_json(msg="One IP in cluster_ips must be IPv4 and other IPv6")

    ip_validation = \
        Validators.ip_address if len(ip_families) != 1 else \
        Validators.ipv4_address if ip_families[0] == 'IPv4' else \
        Validators.ipv6_address

    ip_validation_msg = \
        Validators.ip_address_msg if len(ip_families) != 1 else \
        Validators.ipv4_address_msg if ip_families[0] == 'IPv4' else \
        Validators.ipv6_address_msg

    for i, cluster_ip_item in enumerate(cluster_ips):

        if not (cluster_ip_item in (None, "None", "") or ip_validation(cluster_ip_item)):
            module.fail_json(msg=f'cluster_ips[{i}] {ip_validation_msg}, None or "" when "ip_families" is'
                                 f' {ip_families or "not specified"}')

    if not (cluster_ip in (None, "None", "") or ip_validation(cluster_ip)):
        module.fail_json(msg=f'cluster_ip {ip_validation_msg}, None or "" when "ip_families" is'
                             f' {ip_families or "not specified"}')

    for i, external_ip in enumerate(spec.get('externalIPs') or []):
        if not Validators.ip_address(external_ip):
            module.fail_json(msg=f'external_ips[{i}] {Validators.ip_address_msg}')

    if service_type != 'LoadBalancer' and (spec.get('loadBalancerIP') or
                                           spec.get('loadBalancerSourceRanges') or
                                           spec.get('loadBalancerClass')):
        module.fail_json(msg="load_balancer_ip, load_balancer_source_ranges and load_balancer_class "
                             "are only valid with type='LoadBalancer'")

    if not Validators.ip_address(spec.get('loadBalancerIP')):
        module.fail_json(msg=f'load_balancer_ip {Validators.ip_address_msg}')
    for i, ip_range in enumerate(spec.get('load_balancer_source_ranges') or list()):
        if not Validators.ip_range(ip_range):
            module.fail_json(msg=f'load_balancer_source_ranges[{i}] {Validators.ip_range_msg}')

    external_name = spec.get('externalName')
    if external_name:
        if service_type != 'ExternalName':
            module.fail_json(msg="external_name is only valid with type='ExternalName'")
        if not Validators.dns_subdomain(external_name):
            module.fail_json(msg=f'external_name {Validators.dns_subdomain_msg}')

    health_check_node_port = spec.get('healthCheckNodePort')
    external_traffic_policy = spec.get('externalTrafficPolicy')
    if health_check_node_port:
        if not (service_type == 'LoadBalancer' and external_traffic_policy == 'Local'):
            module.fail_json(msg="health_check_node_port is only valid with type='LoadBalancer' "
                                 "and external_traffic_policy='Local'")
        if not Validators.port(health_check_node_port):
            module.fail_json(msg=f'health_check_node_port {Validators.port_msg}')

    session_affinity_timeout = spec.get('sessionAffinityConfig').get('clientIP').get('timeoutSeconds')

    # "user defined session_affinity_timeout" is almost the same as
    # "session_affinity_timeout is not set to default value"
    if session_affinity_timeout != 10800 and spec.get('sessionAffinity') != 'ClientIP':
        module.fail_json("session_affinity_timeout can only be used with session_affinity='ClientIP'")
    if not 0 < session_affinity_timeout <= 86400:
        module.fail_json(msg='session_affinity_timeout must be 0 < x <= 86400')


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        selector=dict(type='dict'),
        ports=dict(type='list', elements='dict', options=dict(
            port=dict(type='int', required=True),
            target_port=dict(type='str'),
            protocol=dict(type='str', choices=['UDP', 'TCP', 'SCTP'], default='TCP'),
            name=dict(type='str'),
            node_port=dict(type='int')
        )),
        type=dict(type='str', default='ClusterIP', choices=['ExternalName', 'ClusterIP', 'NodePort', 'LoadBalancer']),
        ip_families=dict(type='list', elements='str', choices=['IPv4', 'IPv6']),
        ip_families_policy=dict(type='str', choices=['SingleStack', 'PreferDualStack', 'RequireDualStack'], ),
        cluster_ip=dict(type='str'),
        cluster_ips=dict(type='list', elements='str'),
        external_ips=dict(type='list', elements='str'),
        load_balancer_ip=dict(type='str'),
        load_balancer_source_ranges=dict(type='list', elements='str'),
        load_balancer_class=dict(type='str'),
        external_name=dict(type='str'),
        external_traffic_policy=dict(type='str', choices=['Local', 'Cluster']),
        internal_traffic_policy=dict(type='str', choices=['Local', 'Cluster'], default='Cluster'),
        health_check_node_port=dict(type='int'),
        publish_not_ready_addresses=dict(type='bool', default=False),
        session_affinity=dict(type='str', choices=['ClientIP', 'None'], default='None'),
        session_affinity_timeout=dict(type='int', default=10800)

    ))
    required_if = [
        ('state', 'present', ('ports',))
    ]
    mutually_exclusive = deepcopy(UPDATE_MUTUALLY_EXCLUSIVE)
    mutually_exclusive.append(('cluster_ip', 'cluster_ips'))

    module = AnsibleModule(argument_spec=argspec,
                           required_if=required_if,
                           mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
