#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: config_map

short_description: Creates k8s ConfigMap

version_added: "1.0.0"

description: Creates k8s ConfigMap which holds configuration data for pods to consume.

extends_documentation_fragment:
    - sodalite.k8s.common_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    data:
        description:
            - Contains the configuration data.
            - Each key must consist of alphanumeric characters, '-', '_' or '.'.
            - Values with non-UTF-8 byte sequences must use the C(binary_data) field.
            - The keys stored in C(data) must not overlap with the keys in the C(binary_data) field, this is enforced
              during validation process.
        type: dict
    binary_data:
        description:
           - Contains the binary data.
           - Each key must consist of alphanumeric characters, '-', '_' or '.'.
           - Can contain byte sequences that are not in the UTF-8 range.
           - The keys stored in C(binary_data) must not overlap with the ones in the C(data) field, this is enforced
             during validation process.
        type: dict
    immutable:
        description:
            - If set to C(true), ensures that data stored in the ConfigMap cannot be updated (only object metadata
              can be modified).
            - If set to C(false), the field can be modified at any time.
        type: bool
        default: false

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''
# TODO fix
EXAMPLES = r'''
# Create new configmap
- name: Config for xOpera rest api
  sodalite.k8s.config_map:
    name: xOpera-config
    data:
      db_ip: postgres-service
# Replace config
- name: Config for xOpera rest api
  sodalite.k8s.config_map:
    name: xOpera-config
    state: present
    force: yes
    data:
      db_ip: mysql-service
# Create config with binary data
- name: Binary config
  sodalite.k8s.config_map:
    name: binary-config
    binary_data:
      db_ip: cG9zdGdyZXMtc2VydmljZQ==
# Create config with metadata
- name: Metadata
  sodalite.k8s.config_map:
    name: xOpera-config
    metadata:
      labels:
        app: postgres
      annotations:
        type: my_config
    data:
      db_ip: postgres-service
# Remove config
- name: Config for xOpera rest api
  sodalite.k8s.config_map:
    name: xOpera-config
    state: absent
    data:
      db_ip: postgres-service
'''

# TODO fix
RETURN = r'''
result:
    description:
    - The created, or otherwise present object. Will be empty in the case of a deletion.
    returned: success
    type: complex
    contains:
        apiVersion:
            description: Api version used for creating ConfigMap
            type: str
            returned: always
            sample: 'v1'
        kind:
            description: ConfigMap
            type: str
            returned: always
            sample: 'ConfigMap'
        metadata:
            description: Standard object's metadata.
            type: dict
            returned: always
        binaryData:
            description: Binary data in ConfigMap
            type: str
            returned: when I(binary_data) is present
        data:
            description: Data in ConfigMap
            type: str
            returned: when I(data) is present
        immutable:
            description: Whether ConfigMap is immutable
            type: bool
            returned: when I(immutable) is present
'''

import copy

from ansible_collections.kubernetes.core.plugins.module_utils.ansiblemodule import AnsibleModule
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import (common_arg_spec, METADATA_ARG_SPEC, COMMON_MUTALLY_EXCLUSIVE)
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Base64, Validators


def definition(params):

    data = params.get('data')
    binary_data = params.get('binary_data')
    metadata = params.get('metadata')

    body = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": params.get('name')
        },
        "immutable": params.get('immutable')
    }
    if binary_data:
        body['binaryData'] = binary_data
    if data:
        body['data'] = data
    if metadata:
        body['metadata'].update(metadata)

    return body


def validate(module, k8s_definition):

    data = k8s_definition.get('data', dict())
    binary_data = k8s_definition.get('binaryData', dict())
    annotations = k8s_definition['metadata'].get('annotations', dict())
    labels = k8s_definition['metadata'].get('labels', dict())

    data_keys_valid = all([Validators.alphanumeric(key) for key in data.keys()])
    binary_data_keys_valid = all([Validators.alphanumeric(key) for key in binary_data.keys()])
    keys_unique = len(set(list(data.keys()) + list(binary_data.keys()))) == len(data.keys()) + len(binary_data.keys())
    binary_data_values_valid = all([Base64.validate(value) for value in binary_data.values()])

    if not data_keys_valid:
        module.fail_json(msg="Keys in data must consist of alphanumeric characters, '-', '_' or '.'")
    if not binary_data_keys_valid:
        module.fail_json(msg="Keys in binary_data must consist of alphanumeric characters, '-', '_' or '.'")
    if not keys_unique:
        module.fail_json(msg="Keys in data and binary_data should not overlap")
    if not binary_data_values_valid:
        module.fail_json(msg="Values in binary_data should be in Base64 format")
    if not Validators.string_string_dict(annotations):
        module.fail_json(msg="Metadata.annotations should be map[string]string")
    if not Validators.string_string_dict(labels):
        module.fail_json(msg="Metadata.labels should be map[string]string")


def main():
    argspec = common_arg_spec()
    argspec.update(copy.deepcopy(METADATA_ARG_SPEC))
    argspec.update(dict(
        data=dict(type='dict'),
        binary_data=dict(type='dict'),
        immutable=dict(type='bool', default=False)
    ))

    module = AnsibleModule(argument_spec=argspec, mutually_exclusive=COMMON_MUTALLY_EXCLUSIVE, supports_check_mode=True)
    from ansible_collections.kubernetes.core.plugins.module_utils.common import (K8sAnsibleMixin, get_api_client)
    from ansible_collections.sodalite.k8s.plugins.module_utils.common import (execute_module)

    configmap_def = definition(module.params)
    validate(module, configmap_def)

    k8s_ansible_mixin = K8sAnsibleMixin(module)
    k8s_ansible_mixin.client = get_api_client(module=module)
    execute_module(module, k8s_ansible_mixin, configmap_def)


if __name__ == '__main__':
    main()
