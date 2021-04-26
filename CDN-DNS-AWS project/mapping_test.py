import unittest
from mappings import *
import random
import socket
import struct


class MyTestCase(unittest.TestCase):
    def test_aws_region(self):
        for m in CDN_MAPPINGS:
            region = find_aws_region(m['ip_address'])
            self.assertEqual(m['region'], region)

    def test_best_cdn_simple(self):
        for m in CDN_MAPPINGS:
            ip = find_best_cdn(m['ip_address'])
            self.assertEqual(m['ip_address'], ip)

    def test_best_cdn_near(self):
        for m in CDN_MAPPINGS:
            client_ip = m['ip_address'][:-1] + '0'
            ip = find_best_cdn(client_ip)
            self.assertEqual(m['ip_address'], ip)

    def test_best_cdn_random_ip(self):
        random_ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        ip = find_best_cdn(random_ip)
        self.assertIsNotNone(ip)
        self.assertEqual(ip, find_best_cdn(ip))


if __name__ == '__main__':
    unittest.main()
