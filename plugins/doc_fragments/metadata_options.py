from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
    metadata:
        description:
        - metadata that all persisted resources must have, which includes all objects users must create.
        - I(name) and I(namespace) should be placed in dedicated arguments
        type: dict
        default: {}
        suboptions:
            labels:
                description:
                - Map of string keys and values that can be used to organize and categorize (scope and select) objects.
                - May match selectors of replication controllers and services.
                - More info U(http://kubernetes.io/docs/user-guide/labels).
                type: dict
            annotations:
                description:
                - Unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata.
                - They are not queryable and should be preserved when modifying objects.
                - More info U(http://kubernetes.io/docs/user-guide/annotations).
                type: dict
'''
