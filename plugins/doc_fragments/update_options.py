from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
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
    apply:
        description:
        - C(apply) compares the desired resource definition with the previously supplied resource definition,
          ignoring properties that are automatically generated
        - C(apply) works better with Services than 'force=yes'
        - mutually exclusive with C(merge_type)
        default: False
        type: bool
'''
