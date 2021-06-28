from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

try:
    from ansible_module.turbo.module import (
        AnsibleTurboModule as AnsibleModule,
    )  # noqa: F401
    AnsibleModule.collection_name = "sodalite.k8s"
except ImportError:
    from ansible.module_utils.basic import AnsibleModule
