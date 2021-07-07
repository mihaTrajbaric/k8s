from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import re


def execute_module(module, k8s_ansible_mixin, resource_definition):

    k8s_ansible_mixin.module = module
    k8s_ansible_mixin.module.params['resource_definition'] = resource_definition

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


class Base64:

    # TODO can it also be done with ansible?

    @staticmethod
    def encode(message):
        return base64.b64encode(message.encode('ascii')).decode('ascii')

    @staticmethod
    def decode(message):
        return base64.b64decode(message.encode('ascii')).decode('ascii')

    @staticmethod
    def validate(message):
        try:
            return Base64.encode(Base64.decode(message)) == message
        except Exception:
            return False


class Validators:

    @staticmethod
    def alphanumeric(value):
        """
        validates that value consist only of alphanumeric characters, '-', '_' or '.'.
        """
        regex = re.compile(r'^[a-zA-Z0-9_.-]+$')
        return bool(regex.match(str(value)))

    @staticmethod
    def string_string_dict(_dict):
        """
        Ensures all values are strings
        """
        if _dict is None:
            return True
        return all([isinstance(value, str) and isinstance(key, str) for key, value in _dict.items()])
