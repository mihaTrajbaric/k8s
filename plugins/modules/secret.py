#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: secret

short_description: Creates k8s Secret

version_added: "1.0.0"

description: Creates k8s Secret, which holds secret data of a certain type.

extends_documentation_fragment:
    - sodalite.k8s.common_update_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

options:
    string_data:
        description:
            - Allows specifying non-binary secret data in string form.
            - It is provided as a write-only input field for convenience.
            - All keys and values are merged into the C(data) field on write, overwriting any existing values.
            - The stringData field is never output when reading from the API.
        type: dict
    data:
        description:
           - Contains the secret data.
           - Each key must consist of alphanumeric characters, '-', '_' or '.'.
           - The serialized form of the secret data is a base64 encoded string, representing the arbitrary
             (possibly non-string) data value here.
        type: dict
    immutable:
        description:
            - If set to C(true), ensures that data stored in the Secret cannot be updated (only object metadata
              can be modified).
            - If set to C(false), the field can be modified at any time.
        type: bool
        default: false
    type:
        description:
            - Used to facilitate programmatic handling of secret data.
        type: str
        default: Opaque

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''
EXAMPLES = r'''
# Create new Secret
- name: Secret for xOpera rest api
  sodalite.k8s.secret:
    name: xOpera-secret
    data:
      db_ip: cG9zdGdyZXMtc2VydmljZQ==
# Replace Secret
- name: Secret for xOpera rest api
  sodalite.k8s.secret:
    name: xOpera-secret
    state: present
    type: Opaque
    force: yes
    data:
      db_ip: bXlzcWwtc2VydmljZQ==
# Create secret with string data
- name: String Secret
  sodalite.k8s.secret:
    name: string-secret
    string_data:
      db_ip: postgres-service
# Create secret with metadata
- name: Labels and annotations
  sodalite.k8s.secret:
    name: xOpera-secret
    labels:
      app: postgres
    annotations:
      type: my_secret
    data:
      db_ip: cG9zdGdyZXMtc2VydmljZQ==
# Remove secret
- name: Secret for xOpera rest api
  sodalite.k8s.secret:
    name: xOpera-secret
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

    body = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        },
        "immutable": params.get('immutable'),
        "type": params.get('type'),
        "stringData": params.get('string_data'),
        "data": params.get('data'),
    }

    return clean_dict(body)


def validate(module, k8s_definition):

    CommonValidation.metadata(module, k8s_definition)

    data = k8s_definition.get('data', dict())
    string_data = k8s_definition.get('stringData', dict())

    data_keys_valid = all([Validators.alnum_ext(key) for key in data.keys()])
    string_data_keys_valid = all([Validators.alnum_ext(key) for key in string_data.keys()])

    if not data_keys_valid:
        module.fail_json(msg="Keys in data must consist of alphanumeric characters, '-', '_' or '.'")
    if not string_data_keys_valid:
        module.fail_json(msg="Keys in string_data must consist of alphanumeric characters, '-', '_' or '.'")
    if not Validators.string_byte_dict(data):
        module.fail_json(msg="data should be map[string][]byte")
    if not Validators.string_string_dict(string_data):
        module.fail_json(msg="string_data should be map[string]string")


def main():
    argspec = update_arg_spec()
    argspec.update(dict(
        data=dict(type='dict'),
        string_data=dict(type='dict'),
        type=dict(type='str', default='Opaque'),
        immutable=dict(type='bool', default=False)
    ))

    module = AnsibleModule(argument_spec=argspec, mutually_exclusive=UPDATE_MUTUALLY_EXCLUSIVE, supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    secret_def = definition(module.params)
    if module.params.get('state') != 'absent':
        validate(module, secret_def)
    execute_module(module, secret_def)


if __name__ == '__main__':
    main()
