from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
    selector:
        description:
        - A label query over a set of resources.
        - The result of C(match_labels) and C(match_expressions) are ANDed.
        - An empty label selector matches all objects.
        - A null label selector matches no objects.
        type: dict
        suboptions:
            match_labels:
                description:
                - A map of {C(key),C(value)} pairs.
                - A single {C(key),C(value)} in the I(match_labels) map is equivalent to an element of
                  I(match_expressions), whose key field is C(key), the operator is C(In), and the values array contains
                  only C(value).
                - The requirements are ANDed.
                type: dict
            match_expressions:
                description:
                - A list of label selector requirements.
                - The requirements are ANDed.
                - A label selector requirement is a selector that contains values, a key, and an operator that relates
                  the key and values.
                type: list
                elements: dict
                suboptions:
                    key:
                        description:
                        - The label key that the selector applies to.
                        - Patch strategy is merge on I(key=key)
                        type: str
                        required: yes
                    operator:
                        description:
                        - Represents a key's relationship to a set of values.
                        type: str
                        choices: [In, NotIn, Exists, DoesNotExist]
                        required: yes
                    values:
                        description:
                        - An array of string values.
                        - If the I(operator=In) or I(operator=NotIn), the values array must be non-empty.
                        - If the I(operator=Exists) or I(operator=DoesNotExist), the values array must be empty.
                        - This array is replaced during a strategic merge patch.
                        type: list
                        elements: str
'''
