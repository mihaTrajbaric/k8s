from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64
import re
import ipaddress


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

    dns_subdomain_msg = "should be a valid lowercase RFC 1123 subdomain. It must consist of lower case alphanumeric " \
                        "characters, '-' or '.', and must start and end with an alphanumeric character."

    @staticmethod
    def dns_subdomain(value):
        """
        validates that value is a valid DNS Subdomain Name (RFC 1123).
        - contain no more than 253 characters
        - contain only lowercase alphanumeric characters, '-' or '.'
        - start with an alphanumeric character
        - end with an alphanumeric character
        """
        if not value:
            return True

        length_valid = len(value) <= 253
        regex = re.compile(r'^[a-z0-9.-]+$')
        second_constraint = bool(regex.match(str(value)))
        first_char_alnum = value[0].isalnum()
        last_char_alnum = value[-1].isalnum()
        return length_valid and second_constraint and first_char_alnum and last_char_alnum

    dns_label_1123_msg = "should be a valid lowercase RFC 1123 DNS Label Name. It must not be longer then 63 " \
                         "characters, must consist of lower case alphanumeric characters or '-' and must start and " \
                         "end with an alphanumeric character"

    @staticmethod
    def dns_label_1123(value):
        """
        validates that value is a valid DNS Label Name (RFC 1123).
        - contain at most 63 characters
        - contain only lowercase alphanumeric characters or '-'
        - start with an alphanumeric character
        - end with an alphanumeric character
        """
        if not value:
            return True

        length_valid = len(value) <= 63
        regex = re.compile(r'^[a-z0-9-]+$')
        second_constraint = bool(regex.match(str(value)))
        first_char_alnum = value[0].isalnum()
        last_char_alnum = value[-1].isalnum()
        return length_valid and second_constraint and first_char_alnum and last_char_alnum

    dns_label_1035_msg = "should be a valid lowercase RFC 1135 DNS Label Name. It must not be longer then 63 " \
                         "characters, must consist of lower case alphanumeric characters or '-' must start with " \
                         "alphabetic character and end with an alphanumeric character."

    @staticmethod
    def dns_label_1035(value):
        """
        validates that value is a valid DNS Label Name (RFC 1035).
        - contain at most 63 characters
        - contain only lowercase alphanumeric characters or '-'
        - start with an alphabetic character
        - end with an alphanumeric character
        """
        if not value:
            return True

        first_char_alpha = value[0].isalpha()
        return Validators.dns_label_1123(value) and first_char_alpha

    # if not specified otherwise, DNS_LABEL means RFC 1123 DNS_LABEL
    dns_label_msg = dns_label_1123_msg
    dns_label = dns_label_1123

    iana_svc_name_msg = "should be a valid IANA_SVC_NAME : An alphanumeric (a-z, and 0-9) string, with a maximum " \
                        "length of 15 characters, with the '-' character allowed anywhere except the first or the " \
                        "last character or adjacent to another '-' character, it must contain at least a (a-z) " \
                        "character"

    @staticmethod
    def iana_svc_name(value):
        """
        validates port_name is a valid IANA_SVC_NAME (RFC 6335).
        - contains at most 15 characters
        - contains only lowercase alphanumeric characters or '-'
        - starts with an alphanumeric character
        - ends with an alphanumeric character
        - '--' not allowed
        - contains at least a (a-z)
        """
        if not value:
            return True
        length_valid = len(value) <= 15
        regex = re.compile(r'^[a-z0-9-]+$')
        second_constraint = bool(regex.match(str(value)))
        first_last_alpha = value[0].isalnum() and value[-1].isalnum()
        no_adjacent_hyphens = '--' not in value
        one_alpha = any(char.isalpha() for char in value)

        return length_valid and second_constraint and first_last_alpha and no_adjacent_hyphens and one_alpha

    c_identifier_msg = "should be a a valid C_IDENTIFIER. It must start with alphabetic character or '_', followed " \
                       "by a string of alphanumeric characters or '_'"

    @staticmethod
    def c_identifier(value):
        """
        Ensures value is a valid C_IDENTIFIER
        - contains only alphanumeric characters or '_'
        - starts with alphabetic character or '_'
        """
        regex = re.compile(r'[A-Za-z_][A-Za-z0-9_]*$')
        return bool(regex.match(str(value)))

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
        regex = re.compile(r'^([+-]?[0-9.]+)([eEinumkKMGTP]*[-+]?[0-9]*)$')
        return bool(regex.match(str(string)))

    @staticmethod
    def string_quantity_dict(_dict):
        """
        Ensures all keys are strings and all values are quantity
        """
        if _dict is None:
            return True
        return all([isinstance(key, str) and isinstance(value, str) and Validators.quantity(value)
                    for key, value in _dict.items()])

    port_msg = "should be a valid port number, 0 < x < 65536"

    @staticmethod
    def port(x):
        """
        Validates 0 < x < 65536
        """
        if x is None:
            return True
        return 0 < x < 65536

    ip_address_msg = "should be a valid IPv4 or IPv6 address"

    @staticmethod
    def ip_address(address):
        """
        Validates ip address (IPv4 or IPv6)
        """
        if address is None:
            return True
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    ipv4_address_msg = "should be a valid IPv4 address"

    @staticmethod
    def ipv4_address(address):
        """
        Validates IPv4 address
        """
        if address is None:
            return True
        try:
            ipaddress.IPv4Address(address)
            return True
        except ValueError:
            return False

    ipv6_address_msg = "should be a valid IPv6 address"

    @staticmethod
    def ipv6_address(address):
        """
        Validates IPv6 address
        """
        if address is None:
            return True
        try:
            ipaddress.IPv6Address(address)
            return True
        except ValueError:
            return False

    ip_range_msg = "should be a valid IPv4 (e.g. '143.231.0.0/16') " \
                   "or IPv6 (e.g. 2001:db8:abcd:0012::0/64) IP range (CIDR block)"

    @staticmethod
    def ip_range(ip_range):
        """
        Validates IP range
        """
        if ip_range is None:
            return True
        try:
            ipaddress.ip_network(ip_range)
            return True
        except ValueError:
            return False


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

    @staticmethod
    def selector(module, k8s_definition):
        """
        validates spec.selector section
        """
        if 'selector' in k8s_definition['spec'].keys():
            match_expressions = k8s_definition['spec']['selector'].get('matchExpressions', list())
            for expression in match_expressions:
                valid_operators = ('In', 'NotIn', 'Exists', 'DoesNotExist')
                operator = expression.get('operator')
                if operator not in valid_operators:
                    module.fail_json(msg="Every selector.match_expressions.operator should be chosen "
                                         "from {0}".format({', '.join(valid_operators)}))
                values_condition = (operator in ('In', 'NotIn')) == bool(expression.get('values'))
                if not values_condition:
                    module.fail_json(msg="If in any selector.match_expressions operator is 'In' or 'NotIn', the values "
                                         "array must be non-empty. If operator is 'Exists' or 'DoesNotExist', the "
                                         "values array must be empty.")
            match_labels = k8s_definition['spec']['selector'].get('matchLabels', dict())
            if not Validators.string_string_dict(match_labels):
                module.fail_json(msg="Selector.match_labels should be map[string]string")
