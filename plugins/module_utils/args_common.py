from __future__ import (absolute_import, division, print_function)
from ansible_collections.kubernetes.core.plugins.module_utils.args_common import (
    AUTH_ARG_SPEC, WAIT_ARG_SPEC, DELETE_OPTS_ARG_SPEC)

import copy

__metaclass__ = type

COMMON_ARG_SPEC = dict(
    state=dict(
        default='present',
        choices=['present', 'absent', 'patched']
    ),
    name=dict(
        type='str',
        required=True
    ),
    namespace=dict(
        type='str',
        default='default'
    )
)

UPDATE_ARG_SPEC = dict(
    force=dict(
        type='bool',
        default=False
    ),
    merge_type=dict(
        type='list',
        elements='str',
        choices=['json', 'merge', 'strategic-merge']
    ),
    apply=dict(
        type='bool',
        default=False
    )
)

METADATA_ARG_SPEC = dict(
    labels=dict(type='dict'),
    annotations=dict(type='dict')
)


def common_arg_spec():
    argument_spec = copy.deepcopy(COMMON_ARG_SPEC)
    argument_spec.update(copy.deepcopy(AUTH_ARG_SPEC))
    argument_spec.update(copy.deepcopy(WAIT_ARG_SPEC))
    argument_spec.update(copy.deepcopy(METADATA_ARG_SPEC))
    argument_spec['delete_options'] = dict(type='dict', default=None, options=copy.deepcopy(DELETE_OPTS_ARG_SPEC))
    return argument_spec


def update_arg_spec():
    argument_spec = common_arg_spec()
    argument_spec.update(copy.deepcopy(UPDATE_ARG_SPEC))
    return argument_spec


UPDATE_MUTUALLY_EXCLUSIVE = [
    ('merge_type', 'apply')
]
