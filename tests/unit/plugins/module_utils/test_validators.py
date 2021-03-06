from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.sodalite.k8s.plugins.module_utils.common import Validators


def test_config_map_key():
    assert Validators.config_map_key('foo-bar')
    assert Validators.config_map_key('foo_bar')
    assert Validators.config_map_key('foo.bar')
    assert Validators.config_map_key('FooBar')
    assert Validators.config_map_key('Foo.Bar-foo_bar')
    assert not Validators.config_map_key('#foo+bar')


def test_dns_subdomain():
    assert Validators.dns_subdomain('a' * 253)
    assert not Validators.dns_subdomain('a' * 254)
    assert not Validators.dns_subdomain("aA3Bd2s")
    assert not Validators.dns_subdomain("ab3d_a")
    assert Validators.dns_subdomain("3abd2a2")
    assert Validators.dns_subdomain("foo-bar.foo-35-bar")


def test_dns_subdomain_wildcard():
    assert Validators.dns_subdomain_wildcard('a' * 253)
    assert not Validators.dns_subdomain_wildcard('a' * 254)
    assert Validators.dns_subdomain_wildcard('foo.bar.com')
    assert Validators.dns_subdomain_wildcard('*.foo.bar.com')
    assert not Validators.dns_subdomain_wildcard('**.foo.bar.com')
    assert not Validators.dns_subdomain_wildcard('a*.foo.bar.com')
    assert not Validators.dns_subdomain_wildcard('*')


def test_dns_label():
    assert Validators.dns_label('a' * 63)
    assert not Validators.dns_label('a' * 64)
    assert not Validators.dns_label("aA3Bd2s")
    assert not Validators.dns_label("ab3d_a")
    assert not Validators.dns_label("ab3d.a")
    assert Validators.dns_label("3abd2a3")
    assert Validators.dns_label("foo-bar-foo-35-bar")


def test_dns_label_1035():
    assert Validators.dns_label_1035('a' * 63)
    assert not Validators.dns_label_1035('a' * 64)
    assert not Validators.dns_label_1035("aA3Bd2s")
    assert not Validators.dns_label_1035("ab3d_a")
    assert not Validators.dns_label_1035("ab3d.a")
    assert not Validators.dns_label_1035("3abd2a3")
    assert Validators.dns_label_1035("abd2a3")
    assert Validators.dns_label_1035("foo-bar-foo-35-bar")


def test_iana_svc_name():
    assert Validators.iana_svc_name('a' * 15)
    assert not Validators.iana_svc_name('a' * 16)
    assert not Validators.iana_svc_name('aAdfA')
    assert not Validators.iana_svc_name('aAd_fA')
    assert not Validators.iana_svc_name('aAd.fA')
    assert not Validators.iana_svc_name('-asdf')
    assert not Validators.iana_svc_name('asdf-')
    assert not Validators.iana_svc_name('as--df')
    assert not Validators.iana_svc_name('5')
    assert Validators.iana_svc_name('a5b6-a')


def test_c_identifier():
    assert not Validators.c_identifier('as3.a')
    assert not Validators.c_identifier('as3-a')
    assert not Validators.c_identifier('3as_a')
    assert Validators.c_identifier('as4_a')
    assert Validators.c_identifier('_as4_a')


def test_string_string_dict():
    assert Validators.string_string_dict({
        'foo': 'bar',
        'foo2': 'bar2'
    })
    assert not Validators.string_string_dict({
        'foo': 1,
    })
    assert not Validators.string_string_dict({
        'foo': {
            'foo': 'bar'
        },
    })


def test_string_byte_dict():
    assert Validators.string_byte_dict({
        'foo': 'YmFy',  # bar in Base64
        'foo2': 'YmFyMg=='
    })
    assert not Validators.string_byte_dict({
        'foo': 1
    })
    assert not Validators.string_byte_dict({
        'foo': 'bar'
    })
    assert not Validators.string_byte_dict({
        'foo': {
            'foo': 'YmFy'
        },
    })


def test_base64():
    assert Validators.base64('cG9zdGdyZXM=')
    assert not Validators.base64('foo')


def test_quantity():
    # memory quantities
    assert Validators.quantity('5Gi')
    assert Validators.quantity('5E')
    assert Validators.quantity('5P')
    assert Validators.quantity('5T')
    assert Validators.quantity('5G')
    assert Validators.quantity('5M')
    assert Validators.quantity('5K')
    assert Validators.quantity('5Ei')
    assert Validators.quantity('5Pi')
    assert Validators.quantity('5Ti')
    assert Validators.quantity('5Gi')
    assert Validators.quantity('5Mi')
    assert Validators.quantity('5Ki')

    # cpu quantities
    assert Validators.quantity('2')
    assert Validators.quantity('0.2')
    assert Validators.quantity('100m')


def string_quantity_dict():
    assert Validators.string_quantity_dict({
        'foo': '5Gi'
    })
    assert not Validators.string_quantity_dict({
        'foo': 4
    })
    assert not Validators.string_quantity_dict({
        3: '4'
    })


def test_port():
    assert not Validators.port(-1)
    assert not Validators.port(0)
    assert Validators.port(1)
    assert Validators.port(65535)
    assert not Validators.port(65536)


def test_ip_address():
    assert Validators.ip_address('192.168.1.1')
    assert Validators.ip_address('2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF')
    assert not Validators.ip_address('192.168.1.315')
    assert not Validators.ip_address('a')


def test_ipv4_address():
    assert Validators.ipv4_address('192.168.1.1')
    assert not Validators.ipv4_address('2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF')
    assert not Validators.ipv4_address('192.168.1.315')
    assert not Validators.ipv4_address('a')


def test_ipv6_address():
    assert not Validators.ipv6_address('192.168.1.1')
    assert Validators.ipv6_address('2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF')
    assert not Validators.ipv6_address('2001:db8:3333:4444:CCCC:DDDD:EEEE:FFFF:AAAA')
    assert not Validators.ipv6_address('a')


def test_ip_range():
    assert Validators.ip_range('192.168.1.0/24')
    assert not Validators.ip_range('192.168.1.0/33')
    assert not Validators.ip_range('a')
    assert Validators.ip_range('::/0')
    assert Validators.ip_range('2001:db8::/128')
    assert not Validators.ip_range('2001:db8::/129')
