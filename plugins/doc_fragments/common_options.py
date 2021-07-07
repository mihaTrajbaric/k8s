from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
    state:
        description:
        - Determines if an object should be created, or deleted. When set to C(present), an object will be
          created, if it does not already exist. If set to C(absent), an existing object will be deleted. If set to
          C(present), an existing object will be patched, if its attributes differ from those specified as module params.
        type: str
        default: present
        choices: [ absent, present ]
    name:
        description:
        - Use to specify an object name.
        - Use to create, delete, or discover an object without providing a full resource definition.
        - Use in conjunction with I(namespace) to identify a specific object.
        type: str
        required: True
    namespace:
        description:
        - Use to specify an object namespace.
        - Use in conjunction with I(name) to identify a specific object.
        type: str
        default: default
    force:
        description:
        - If set to C(yes), and I(state) is C(present), an existing object will be replaced.
        type: bool
        default: no
    merge_type:
        description:
        - Whether to override the default patch merge approach with a specific type. By default, the strategic
          merge will typically be used.
        - For example, Custom Resource Definitions typically aren't updatable by the usual strategic merge. You may
          want to use C(merge) if you see "strategic merge patch format is not supported"
        - See U(https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/#use-a-json-merge-patch-to-update-a-deployment)
        - If more than one C(merge_type) is given, the merge_types will be tried in order. This defaults to
          C(['strategic-merge', 'merge']), which is ideal for using the same parameters on resource kinds that
          combine Custom Resources and built-in resources.
        - mutually exclusive with C(apply)
        - I(merge_type=json) is deprecated and will be removed in version 3.0.0. Please use M(kubernetes.core.k8s_json_patch) instead.
        choices:
        - json
        - merge
        - strategic-merge
        type: list
        elements: str
    validate:
        description:
        - how (if at all) to validate the resource definition against the kubernetes schema.
          Requires the kubernetes-validate python module.
        suboptions:
          fail_on_error:
            description: whether to fail on validation errors.
            type: bool
          version:
            description: version of Kubernetes to validate against. defaults to Kubernetes server version
            type: str
          strict:
            description: whether to fail when passing unexpected properties
            default: True
            type: bool
        type: dict
    append_hash:
        description:
        - Whether to append a hash to a resource name for immutability purposes
        - Applies only to ConfigMap and Secret resources
        - The parameter will be silently ignored for other resource kinds
        - The full definition of an object is needed to generate the hash - this means that deleting an object created
          with append_hash will only work if the same object is passed with state=absent (alternatively, just use
          state=absent with the name including the generated hash and append_hash=no)
        default: False
        type: bool
    apply:
        description:
        - C(apply) compares the desired resource definition with the previously supplied resource definition,
          ignoring properties that are automatically generated
        - C(apply) works better with Services than 'force=yes'
        - mutually exclusive with C(merge_type)
        default: False
        type: bool
requirements:
  - "python >= 3.6"
  - "kubernetes >= 12.0.0"
  - "PyYAML >= 3.11"
  - "jsonpatch"
'''
