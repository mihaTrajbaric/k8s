from __future__ import absolute_import, division, print_function
__metaclass__ = type

import base64
import re


class Base64:

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


class Quantity:

    @staticmethod
    def validate():
        pass


class Validators:

    @staticmethod
    def alnum_ext(value):
        """
        validates that value consist only of alphanumeric characters, '-', '_' or '.'.
        """
        regex = re.compile(r'^[a-zA-Z0-9_.-]+$')
        return bool(regex.match(str(value)))

    @staticmethod
    def dns_subdomain(value):
        """
        validates that value is a valid DNS Subdomain Name (RFC 1123).
        - contain no more than 253 characters
        - contain only lowercase alphanumeric characters, '-' or '.'
        - start with an alphanumeric character
        - end with an alphanumeric character
        """

        length_valid = len(value) <= 253
        regex = re.compile(r'^[a-z0-9.-]+$')
        second_constraint = bool(regex.match(str(value)))
        first_char_alpha = value[0].isalpha()
        last_char_alpha = value[-1].isalpha()
        return length_valid and second_constraint and first_char_alpha and last_char_alpha

    @staticmethod
    def dns_label(value):
        """
        validates that value is a valid DNS Label Name (RFC 1123).
        - contain at most 63 characters
        - contain only lowercase alphanumeric characters or '-'
        - start with an alphanumeric character
        - end with an alphanumeric character
        """

        length_valid = len(value) <= 63
        regex = re.compile(r'^[a-z0-9-]+$')
        second_constraint = bool(regex.match(str(value)))
        first_char_alpha = value[0].isalpha()
        last_char_alpha = value[-1].isalpha()
        return length_valid and second_constraint and first_char_alpha and last_char_alpha

    @staticmethod
    def string_string_dict(_dict):
        """
        Ensures all keys and values are strings
        """
        if _dict is None:
            return True
        return all([isinstance(value, str) and isinstance(key, str) for key, value in _dict.items()])

    @staticmethod
    def string_byte_dict(_dict):
        """
        Ensures all keys are strings and all values are base64
        """
        if _dict is None:
            return True
        return all([isinstance(value, str) and Validators.base64(value) for key, value in _dict.items()])

    @staticmethod
    def base64(message):
        return Base64.validate(message)

    @staticmethod
    def quantity(string):
        # TODO implement quantity validation
        return True

    @staticmethod
    def string_quantity_dict(_dict):
        """
        Ensures all keys are strings and all values are quantity
        """
        if _dict is None:
            return True
        return all([isinstance(value, str) and Validators.quantity(value) for key, value in _dict.items()])


class CommonValidation:

    @staticmethod
    def metadata(module, k8s_definition):
        """
        validates metadata
        """
        annotations = k8s_definition['metadata'].get('annotations', dict())
        labels = k8s_definition['metadata'].get('labels', dict())
        if not Validators.string_string_dict(annotations):
            module.fail_json(msg="Annotations should be map[string]string")
        if not Validators.string_string_dict(labels):
            module.fail_json(msg="Labels should be map[string]string")
