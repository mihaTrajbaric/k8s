from __future__ import (absolute_import, division, print_function)

COMMON_ARG_SPEC = {
    'state': {
        'default': 'present',
        'choices': ['present', 'absent'],
    },
    'name': {
        'type': 'str',
        'required': True
    },
    'namespace': {
        'type': 'str',
        'default': 'default'
    },
    'force': {
        'type': 'bool',
        'default': False,
    },
    'apply': {
        'type': 'bool',
        'default': False,
    },
}
