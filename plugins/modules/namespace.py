#!/usr/bin/python

# Copyright: (c) 2021, Mihael Trajbarič <mihael.trajbaric@xlab.si>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: namespace

short_description: Creates k8s Namespace

version_added: "1.0.0"

description: Creates k8s Namespace, which are virtual clusters backed by the same physical cluster. Namespaces are a
             way to divide cluster resources between multiple users. They provide a scope for names. Names of resources
             need to be unique within a namespace, but not across namespaces. Each Kubernetes resource can only be in
             one namespace. Default namespace is called 'default'.

extends_documentation_fragment:
    - sodalite.k8s.common_update_options
    - sodalite.k8s.metadata_options
    - kubernetes.core.k8s_auth_options
    - kubernetes.core.k8s_wait_options
    - kubernetes.core.k8s_delete_options

seealso:
- name: K8s Namespace documentation
  description: Complete namespace documentation on kubernetes website
  link: https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/
- name: K8s Namespace API reference
  description: API reference for K8s Namespace resource on kubernetes website
  link: https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/namespace-v1/

author:
    - Mihael Trajbarič (@mihaTrajbaric)
'''
EXAMPLES = r'''
- name: Create new namespace
  sodalite.k8s.namespace:
    name: test-namespace
    state: present

- name: Add labels and annotations
  sodalite.k8s.namespace:
    name: test-namespace
    state: patched
    labels:
        foo: bar
    annotations:
        foo2: bar2

- name: Delete namespace
  sodalite.k8s.namespace:
    name: test-namespace
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
        "kind": "Namespace",
        "metadata": {
            "name": params.get('name'),
            "labels": params.get('labels'),
            "annotations": params.get('annotations')
        }
    }

    return clean_dict(body)


def validate(module, k8s_definition):

    CommonValidation.metadata(module, k8s_definition)

    if not Validators.dns_subdomain(k8s_definition['metadata']['name']):
        module.fail_json(msg=f"'name' {Validators.dns_subdomain_msg}")


def main():
    argspec = update_arg_spec()

    module = AnsibleModule(argument_spec=argspec, mutually_exclusive=UPDATE_MUTUALLY_EXCLUSIVE, supports_check_mode=True)
    from ansible_collections.sodalite.k8s.plugins.module_utils.k8s_connector import execute_module

    k8s_def = definition(module.params)
    validate(module, k8s_def)

    execute_module(module, k8s_def)


if __name__ == '__main__':
    main()
