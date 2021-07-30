#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type
DOCUMENTATION = r'''
---
module: ingress

short_description: Creates k8s Ingress

version_added: "1.0.0"

description: Creates k8s Ingress, which is s a collection of rules that allow inbound connections to reach the
             endpoints defined by a backend. An Ingress can be configured to give services externally-reachable
             urls, load balance traffic, terminate SSL, offer name based virtual hosting etc.

extends_documentation_fragment:
    - sodalite.k8s.common_update_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    ingress_class_name:
        description:
        - The name of the IngressClass cluster resource.
        - The associated IngressClass defines which controller will implement the resource.
        - This replaces the deprecated kubernetes.io/ingress.class annotation.
         - For backwards compatibility, when that annotation is set, it must be given precedence over this field.
         - The controller may emit a warning if the field and annotation have different values.
        type: str
    default_backend_service:
        description:
        - The service backend that should handle requests that don't match any rule.
        - If I(rules) are not specified, I(default_backend_service) must be specified.
        - If I(default_backend_service) is not set, the handling of requests that do not match any of the rules will be
          up to the Ingress controller.
        type: dict
        suboptions:
            name:
                description:
                - Name of the referenced service.
                - The service must exist in the same namespace as the Ingress object.
                type: str
                required: true
            port:
                description:
                - A port name or port number of the port on the Service.
                - Number must be a valid port number (0 < x < 65536).
                - Name must be an IANA_SVC_NAME.
                type: str
                required: true
    rules:
        description:
        - A list of host rules used to configure the Ingress.
        - If unspecified, or no rule matches, all traffic is sent to the default backend.
        type: list
        elements: dict
        suboptions:
            host:
                description:
                - Host is the fully qualified domain name of a network host, as defined by RFC 3986.
                - IPs and ports are not allowed.
                - Implicit port is set to C(80) (http) and C(443) (https).
                - If I(host) is unspecified, the Ingress routes all traffic based on paths.
                - Host can be "precise" which is a domain name without the terminating dot of a network host (e.g.
                  "foo.bar.com") or "wildcard", which is a domain name prefixed with a single wildcard label (e.g.
                  "*.foo.com").
                - You cannot have a wildcard label by itself (e.g. Host == "*").
                - Some k8s distros do not support wildcard
                type: str
            paths:
                description:
                - A collection of paths that map requests to backends.
                - Incoming urls matching the path are forwarded to the backend.
                required: true
                type: list
                elements: dict
                suboptions:
                    backend_service:
                        description:
                        - The referenced service endpoint to which the traffic will be forwarded to.
                        type: dict
                        required: true
                        suboptions:
                            name:
                                description:
                                - Name of the referenced service.
                                - The service must exist in the same namespace as the Ingress object.
                                type: str
                                required: true
                            port:
                                description:
                                - A port name or port number of the port on the Service.
                                - Number must be a valid port number (0 < x < 65536).
                                - Name must be an IANA_SVC_NAME.
                                required: true
                                type: str
                    path:
                        description:
                        - Path to be matched  against the path of an incoming request.
                        - It should follow "path" part of a URL as defined by RFC 3986, but this is currently
                          not validated.
                        - Must begin with a '/'.
                        - When unspecified, all paths from incoming requests are matched.
                        default: '/'
                        type: str
                    path_type:
                        description:
                        - Determines the interpretation of the I(path) matching.
                        - I(path_type=Exact) matches the URL path exactly.
                        - I(path_type=Prefix) matches based on a URL path prefix split by '/'.
                        type: str
                        default: Prefix
                        choices: [ Exact, Prefix ]
    tls:
        description:
        - TLS configuration.
        - Currently the Ingress only supports a single TLS port, 443.
        - If multiple members of this list specify different hosts, they will be multiplexed on the same port according
          to the hostname specified through the SNI TLS extension, if the ingress controller fulfilling the ingress
          supports SNI.
        type: list
        elements: dict
        suboptions:
            hosts:
                description:
                - A list of hosts included in the TLS certificate.
                - The values in this list must match the name/s used in the tlsSecret.
                - Defaults to the wildcard host setting for the loadbalancer controller fulfilling this Ingress,
                  if left unspecified.
                - TLS will not work on the default rule because the certificates would have to be issued for all the
                  possible sub-domains. Therefore, hosts in the tls section need to explicitly match the host in
                  the rules section.
                type: list
                elements: str
            secret:
                description:
                - The name of the secret used to terminate TLS traffic on port 443.
                - Field is left optional to allow TLS routing based on SNI hostname alone.
                - If the SNI host in a listener conflicts with the "Host" header field used by an IngressRule,
                  the SNI host is used for termination and value of the Host header is used for routing.
                type: str

seealso:
- name: K8s Ingress documentation
  description: Documentation about K8s Ingress resource on kubernetes website
  link: https://kubernetes.io/docs/concepts/services-networking/ingress/
- name: K8s Ingress API reference
  description: API reference for K8s Ingress resource on kubernetes website
  link: https://kubernetes.io/docs/reference/kubernetes-api/service-resources/ingress-v1/

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''

EXAMPLES = r'''
- name: Create simple ingress with default backend
  sodalite.k8s.ingress:
    name: ingress-minimal
    state: present
    default_backend_service:
      name: default-service
      port: 8080
      
- name: Ingress with prefix path
  sodalite.k8s.ingress:
    name: ingress-path
    state: present
    rules:
    - host: foo.bar.com
      paths:
        - path: /testpath
          path_type: Prefix
          backend_service:
             name: test
             port: 80

- name: Ingress with TLS configuration
  sodalite.k8s.ingress:
    name: ingress-tls
    state: present
    rules:
    - host: https-foo.bar.com
      paths:
        - path: /testpath
          path_type: Prefix
          backend_service:
             name: service1
             port: app-port
    tls:
      - hosts: ['https-foo.bar.com']
        secret: secret-tls

- name: State absent
  sodalite.k8s.ingress:
    name: ingress-test
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


def definition(params):
    # TODO

    def get_port(port, _type):
        """
        makes sure port gets assigned to 'name' or 'number', depending on IntOrString unmarshalling
        """
        unmarshalled_port = Marshalling.unmarshall_int_or_string(port)
        if isinstance(unmarshalled_port, _type):
            return unmarshalled_port
        return None

    def ingress_backend(backend_service):
        if backend_service is None:
            return None
        return {
            "service": {
                "name": backend_service.get('name'),
                "port": {
                    # function get_port(port, _type) will make sure only one of (name, number) != None
                    # (required by mutually exclusive condition)
                    'name': get_port(backend_service.get('port'), str),
                    'number': get_port(backend_service.get('port'), int),
                }
            }
        }

    body = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        "spec": {
            "defaultBackend": ingress_backend(params.get('default_backend_service')),
            "ingressClassName": params.get('ingress_class_name'),
            "rules": [
                {
                    'host': rule.get('host'),
                    'http': {
                        'paths': [
                            {
                                'backend': ingress_backend(path.get('backend_service')),
                                'path': path.get('path'),
                                'pathType': path.get('path_type')
                            }
                            for path in rule.get('paths') or list()
                        ]
                    }
                }
                for rule in params.get('rules') or list()
            ],
            'tls': [
                {
                    'hosts': tls_config.get('hosts'),
                    'secretName': tls_config.get('secret')
                }
                for tls_config in params.get('tls') or list()
            ]
        }
    }

    return clean_dict(body)


def validate(module, k8s_definition):
    CommonValidation.metadata(module, k8s_definition)

    if not Validators.dns_subdomain(k8s_definition['metadata']['name']):
        module.fail_json(msg=f"'name' {Validators.dns_subdomain_msg}")

    spec = k8s_definition.get('spec', dict())
    if not (spec.get('defaultBackend') or spec.get('rules')):
        module.fail_json(msg="At least one of (default_backend_service, rules) must be present. If present, 'rules'"
                             "must contain at least one element")

    default_backend_service = spec.get('defaultBackend', dict()).get('service', dict())
    if not Validators.dns_label_1035(default_backend_service.get('name')):
        module.fail_json(msg=f"default_backend_service.name {Validators.dns_label_1035_msg}")
    if not Validators.port(default_backend_service.get('port', dict()).get('number')):
        module.fail_json(msg=f"default_backend_service.port can be a port name or number. If it is a port number, "
                             f"it {Validators.port_msg}")
    if not Validators.iana_svc_name(default_backend_service.get('port', dict()).get('name')):
        module.fail_json(msg=f"default_backend_service.port can be a port name or number. If it is a port name, "
                             f"it {Validators.iana_svc_name_msg}")

    for i, rule in enumerate(spec.get('rules', list())):
        if not Validators.dns_subdomain_wildcard(rule.get('host')):
            module.fail_json(msg=f'rules[{i}].host {Validators.dns_subdomain_wildcard_msg}')

        paths = rule.get('http', dict()).get('paths')
        if not paths:
            module.fail_json(msg=f'rules[{i}].paths must contain at least one parameter')

        for j, path in enumerate(paths):
            backend_service = path.get('backend').get('service')
            if not Validators.dns_label_1035(backend_service.get('name')):
                module.fail_json(msg=f"rules[{i}].paths[{j}].backend_service.name {Validators.dns_label_1035_msg}")
            if not Validators.port(backend_service.get('port').get('number')):
                module.fail_json(
                    msg=f"rules[{i}].paths[{j}].backend_service.port can be a port name or number. If it is a port "
                        f"number, it {Validators.port_msg}")
            if not Validators.iana_svc_name(backend_service.get('port').get('name')):
                module.fail_json(
                    msg=f"rules[{i}].paths[{j}].backend_service.port can be a port name or number. If it is a port "
                        f"name, it {Validators.iana_svc_name_msg}")
            if not Validators.url_path(path.get('path')):
                module.fail_json(msg=f"rules[{i}].paths[{j}].path {Validators.url_path_msg}")

    for i, tls_conf in enumerate(spec.get('tls', list())):
        if not Validators.dns_subdomain(tls_conf.get('secretName')):
            module.fail_json(f"tls[{i}].secret {Validators.dns_subdomain_msg}")


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        ingress_class_name=dict(type='str'),
        default_backend_service=dict(type='dict', options=dict(
            name=dict(type='str', required=True),
            port=dict(type='str', required=True),
        )),
        rules=dict(type='list', elements='dict', options=dict(
            host=dict(type='str'),
            paths=dict(type='list', required=True, elements='dict', options=dict(
                backend_service=dict(type='dict', required=True, options=dict(
                    name=dict(type='str', required=True),
                    port=dict(type='str', required=True),
                )),
                path=dict(type='str', default='/'),
                path_type=dict(type='str', default='Prefix', choices=['Exact', 'Prefix']),
            ))
        )),
        tls=dict(type='list', elements='dict', options=dict(
            hosts=dict(type='list', elements='str'),
            secret=dict(type='str', no_log=False)
        ))
    ))

    module = AnsibleModule(argument_spec=argspec,
                           mutually_exclusive=UPDATE_MUTUALLY_EXCLUSIVE,
                           supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
