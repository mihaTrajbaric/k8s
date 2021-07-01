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

options:
    data:
        description:
            - Contains the configuration data.
            - Each key must consist of alphanumeric characters, '-', '_' or '.'.
            - Values with non-UTF-8 byte sequences must use the C(binary_data) field.
            - The keys stored in C(data) must not overlap with the keys in the C(binary_data) field, this is enforced during validation process.
        type: dict
    binary_data:
        description:
           - Contains the binary data.
           - Each key must consist of alphanumeric characters, '-', '_' or '.'.
           - Can contain byte sequences that are not in the UTF-8 range.
           - The keys stored in C(binary_data) must not overlap with the ones in the C(data) field, this is enforced during validation process.
        type: dict
    immutable:
        description:
            - If set to C(true), ensures that data stored in the ConfigMap cannot be updated (only object metadata can be modified).
            - If set to C(false), the field can be modified at any time.
        type: bool
        default: false

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''

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
import re

from ansible_collections.sodalite.k8s.plugins.module_utils.ansiblemodule import AnsibleModule
from ansible_collections.sodalite.k8s.plugins.module_utils.args_common import (COMMON_ARG_SPEC, METADATA_ARG_SPEC)
from ansible_collections.sodalite.k8s.plugins.module_utils.common import Base64


def argspec():
    argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
    argument_spec.update(copy.deepcopy(METADATA_ARG_SPEC))
    argument_spec['data'] = dict(type='dict')
    argument_spec['binary_data'] = dict(type='dict')
    argument_spec['immutable'] = dict(type='bool', default=False)

    return argument_spec


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

    def validate_key(value):
        """
        validates that value consist only of alphanumeric characters, '-', '_' or '.'.
        """
        regex = re.compile(r'^[a-zA-Z0-9_.-]+$')
        return bool(regex.match(str(value)))

    def validate_string_string_dict(_dict):
        """
        Ensures all values are strings
        """
        return all([isinstance(value, str) and isinstance(key, str) for key, value in _dict.items()])

    data = k8s_definition.get('data', {})
    binary_data = k8s_definition.get('binaryData', {})
    annotations = k8s_definition['metadata'].get('annotations', {})
    labels = k8s_definition['metadata'].get('labels', {})

    data_keys_valid = all([validate_key(key) for key in data.keys()])
    binary_data_keys_valid = all([validate_key(key) for key in binary_data.keys()])
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
    if not validate_string_string_dict(annotations):
        module.fail_json(msg="Metadata.annotations should be map[string]string")
    if not validate_string_string_dict(labels):
        module.fail_json(msg="Metadata.labels should be map[string]string")


def main():
    module = AnsibleModule(argument_spec=argspec(), supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.common import K8s

    configmap_def = definition(module.params)
    validate(module, configmap_def)
    k8s = K8s(module, configmap_def)
    k8s.execute_module()


if __name__ == '__main__':
    main()
