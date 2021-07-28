#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type
# TODO options
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
        - I(type==ClusterIP) allocates a cluster-internal IP address for load-balancing to endpoints. Endpoints are
          determined by the selector or if that is not specified, by manual construction of an Endpoints object or
          EndpointSlice objects. If I(cluster_ip=None), no virtual IP is allocated and the endpoints are published as
          a set of endpoints rather than a virtual IP.
        - I(type=NodePort) builds on ClusterIP and allocates a port on every node which routes to the same endpoints
          as the clusterIP.
        - I(type=LoadBalancer) builds on NodePort and creates an external load-balancer (if supported in the current
          cloud) which routes to the same endpoints as the clusterIP.
        - I(type=ExternalName) aliases this service to the specified I(external_name).
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
        - This field will be wiped when updating a service to type I(type=ExternalName).
        type: str
        default: SingleStack
        choices: [ SingleStack, PreferDualStack, RequireDualStack ]
    cluster_ip:
        description:
        - The IP address of the service and is usually assigned randomly.
        - If an address is specified manually, is in-range (as per system configuration), and is not in use, it will be
          allocated to the service; otherwise creation of the service will fail.
        - This field may not be changed through updates unless the type field is also being changed to or from
          I(type=ExternalName) (ExternalName requires this field to be blank, otherwise it is optional)
        - Valid values are "None", empty string (""), or a valid IP address.
        - Setting this to "None" makes a "headless service" (no virtual IP), which is useful when direct endpoint
          connections are preferred and proxying is not required.
        - Only applies to types ClusterIP, NodePort, and LoadBalancer.
        - If this field is specified when creating a Service of I(type=ExternalName), creation will fail.
        - This field will be wiped when updating a Service to type ExternalName.
        type: str
    cluster_ips:
        description:
        - A list of IP addresses assigned to this service.
        - Every IP address must follow the same guidelines, as I(cluster_ip).
        - If both I(cluster_ips) and I(cluster_ip) are specified, cluster_ips[0] and cluster_ip must have the same
          value.
        - Unless the "IPv6DualStack" feature gate is enabled, this field is limited to one value, otherwise, it may
          hold a maximum of two entries (dual-stack IPs, in either order). These IPs must correspond to the values of
          the I(ip_families) field.
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
# TODO examples
EXAMPLES = r'''
# Create PersistentVolumeClaim
- name: Create simple PersistentVolumeClaim
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi

# Create PersistentVolumeClaim with match_expressions
- name: PersistentVolumeClaim with matchExpressions selector
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    selector:
        match_expressions:
          - key: app-volume
            operator: In
            values: [postgres, mysql]
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi

# Create PersistentVolumeClaim with match_labels
- name: PersistentVolumeClaim with matchLabels selector
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    selector:
        match_labels:
          app-volume: postgres
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi

# Create PersistentVolumeClaim with ResourceRequirements
- name: PersistentVolumeClaim with storage_request and storage_limit
  sodalite.k8s.pvc:
    name: pvc-test
    state: present
    access_modes:
        - ReadWriteMany
        - ReadWriteOnce
    storage_request: 5Gi
    storage_limit: 10Gi

# Remove PersistentVolumeClaim
- name: Remove pvc
  sodalite.k8s.pvc:
    name: pvc-test
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
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators, CommonValidation
from ansible_collections.sodalite.k8s.plugins.module_utils.helper import clean_dict


def definition(params):
    # TODO
    body = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        'spec': {
            'accessModes': params.get('access_modes'),
            'selector': {
                'matchExpressions': (params.get('selector') or {}).get('match_expressions'),
                'matchLabels': (params.get('selector') or {}).get('match_labels')
            },
            'resources': {
                'requests': {
                    'storage': params.get('storage_request')
                },
                'limits': {
                    'storage': params.get('storage_limit')
                }
            },
            'volumeName': params.get('volume_name'),
            'storageClassName': params.get('storage_class_name'),
            'volumeMode': params.get('volume_mode')
        }
    }
    return clean_dict(body)


def validate(module, k8s_definition):
    # TODO
    CommonValidation.metadata(module, k8s_definition)
    CommonValidation.selector(module, k8s_definition)

    access_modes = k8s_definition['spec'].get('accessModes', list())
    if not access_modes:
        module.fail_json(msg="Access_modes should have at least 1 element")

    access_modes_valid = all([item in ('ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany') for item in access_modes])
    if not access_modes_valid:
        module.fail_json(msg="Elements of access_modes should be chosen from "
                             "('ReadWriteOnce', 'ReadOnlyMany', 'ReadWriteMany')")

    if 'resources' in k8s_definition['spec'].keys():
        limits = k8s_definition['spec']['resources'].get('limits', dict())
        if not Validators.string_quantity_dict(limits):
            module.fail_json(msg="Storage_limit should be map[string]Quantity")

        requests = k8s_definition['spec']['resources'].get('requests', dict())
        if not Validators.string_quantity_dict(requests):
            module.fail_json(msg="Storage_request should be map[string]Quantity")


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        # TODO name: RFC1035 label
        # TODO selector: Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName.
        selector=dict(type='dict'),
        ports=dict(type='list', elements='dict', options=dict(
            port=dict(type='int', required=True),
            # TODO target_port is ignored for services with clusterIP=None, and should be omitted
            #  or set equal to the 'port' field.
            # TODO validate port (0 < x < 65536) (if int)
            # TODO validate IANA_SVC_NAME (if string)
            target_port=dict(type='str'),
            protocol=dict(type='str', choices=['UDP', 'TCP', 'SCTP'], default='TCP'),
            # TODO validate, DNS_LABEL, unique within service
            # TODO optional if only one port on this service, otherwise required
            name=dict(type='str'),
            node_port=dict(type='int')
        )),
        type=dict(type='str', default='ClusterIP', choices=['ExternalName', 'ClusterIP', 'NodePort', 'LoadBalancer']),

        # optional values
        # TODO validate max_len = 2
        # TODO not with ExternalName
        ip_families=dict(type='list', elements='str', choices=['IPv4', 'IPv6']),
        ip_families_policy=dict(type='str', default='SingleStack',
                                choices=['SingleStack', 'PreferDualStack', 'RequireDualStack'], ),

        # TODO validate IP or None or ""
        # TODO not with ExternalName
        # TODO first entry must also go to clusterIP???
        # Max 2 values (but only if cluster_ip)
        cluster_ips=dict(type='list', elements='str'),
        cluster_ip=dict(type='str'),

        # TODO validate IP (v4 or v6)
        external_ips=dict(type='list', elements='str'),

        # TODO only with LoadBalancer
        load_balancer_ip=dict(type='str'),
        load_balancer_source_ranges=dict(type='list', elements='str'),
        load_balancer_class=dict(type='str'),

        # TODO only with ExternalName
        # TODO validate lowercase RFC-1123 hostname
        external_name=dict(type='str'),

        # traffic policies
        external_traffic_policy=dict(type='str', choices=['Local', 'Cluster']),
        internal_traffic_policy=dict(type='str', choices=['Local', 'Cluster'], default='Cluster'),

        # TODO only type == LoadBalancer and external_traffic_policy == Local
        # TODO validate port?
        health_check_node_port=dict(type='int'),
        # TODO verify if true/false is not reversed
        publish_not_ready_addresses=dict(type='bool', default=False),

        # session affinity
        session_affinity=dict(type='str', choices=['ClientIP', 'None'], default='None'),
        # TODO only if session_affinity==ClientIP
        session_affinity_timeout=dict(type='int', default=10800)



    ))
    # required_if = [
    #     ('state', 'present', ('access_modes', 'storage_request'))
    # ]

    module = AnsibleModule(argument_spec=argspec,
                           # required_if=required_if,
                           mutually_exclusive=UPDATE_MUTUALLY_EXCLUSIVE,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
