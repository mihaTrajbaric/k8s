from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.kubernetes.core.plugins.module_utils.common import (K8sAnsibleMixin, get_api_client)


def execute_module(module, resource_definition):
    k8s_ansible_mixin = K8sAnsibleMixin(module)
    k8s_ansible_mixin.client = get_api_client(module=module)

    k8s_ansible_mixin.module = module
    k8s_ansible_mixin.module.params['resource_definition'] = resource_definition
    k8s_ansible_mixin.module.params['validate'] = {'fail_on_error': True}
    if not {'merge_type', 'apply'}.issubset(set(k8s_ansible_mixin.module.params.keys())):
        k8s_ansible_mixin.module.params['merge_type'] = []

    k8s_ansible_mixin.argspec = module.argument_spec
    k8s_ansible_mixin.check_mode = k8s_ansible_mixin.module.check_mode
    k8s_ansible_mixin.params = k8s_ansible_mixin.module.params
    k8s_ansible_mixin.fail_json = k8s_ansible_mixin.module.fail_json
    k8s_ansible_mixin.fail = k8s_ansible_mixin.module.fail_json
    k8s_ansible_mixin.exit_json = k8s_ansible_mixin.module.exit_json
    k8s_ansible_mixin.warn = k8s_ansible_mixin.module.warn
    k8s_ansible_mixin.warnings = []

    k8s_ansible_mixin.kind = resource_definition.get('kind')
    k8s_ansible_mixin.api_version = resource_definition.get('apiVersion')
    k8s_ansible_mixin.name = k8s_ansible_mixin.params.get('name')
    k8s_ansible_mixin.namespace = k8s_ansible_mixin.params.get('namespace')

    k8s_ansible_mixin.check_library_version()
    k8s_ansible_mixin.set_resource_definitions(module)
    k8s_ansible_mixin.execute_module()
