import unittest
from channel import ControlChannel, parse_pasv_message, parse_message
import filecmp

username = 'tuol'
password = 'pUVmMhHuWQgNo9ljknX4'
hostname = 'networks-teaching-ftp.ccs.neu.edu'
control_channel_port = 21


class MyTestCase(unittest.TestCase):
    def setUp(self):
        print()

    def test_control_channel_init(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        self.assertIsNotNone(channel.s)
        channel.close()

    def test_parse_message(self):
        r = '''227 Entering Passive Mode (129,10,111,152,6,129).
'''
        code, m = parse_message(r)
        self.assertEqual("227", code)
        self.assertIsNotNone(m)

    def test_pasv_message_parser(self):
        m = '''Entering Passive Mode (129,10,111,152,6,129).
'''
        ip, port = parse_pasv_message(m)
        self.assertEqual("129.10.111.152", ip)
        self.assertEqual(1665, port)

    def test_list_cmd(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("LIST", "/")
        self.assertIsNotNone(channel.s)
        channel.close()

    def test_mkd_rmd_cmd(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("MKD", "/testDir")
        channel.issue_service_cmd("LIST", "/")
        channel.issue_service_cmd("RMD", "/testDir")
        channel.issue_service_cmd("LIST", "/")
        self.assertIsNotNone(channel.s)
        channel.close()

    def test_retr_cmd(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("LIST", "/")
        channel.issue_service_cmd("RETR", "/hello.txt", "hello.txt")
        self.assertTrue(filecmp.cmp("hello.txt", "hello_original.txt"))
        channel.issue_service_cmd("LIST", "/")
        self.assertIsNotNone(channel.s)
        channel.close()

    def test_stor_dele(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("STOR", "/test.txt", "test.txt")
        channel.issue_service_cmd("RETR", "/test.txt", "test1.txt")
        self.assertTrue(filecmp.cmp("test.txt", "test1.txt"))
        channel.issue_service_cmd("LIST", "/")
        channel.issue_service_cmd("DELE", "/test.txt")
        channel.issue_service_cmd("LIST", "/")
        self.assertIsNotNone(channel.s)
        channel.close()

    def test_mkd_recursive(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("MKD", "/1/2/3")
        channel.issue_service_cmd("RMD", "/1/2/3")
        channel.close()

    def test_stor_recursive(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("STOR", "/x/y/z/test.txt", "other-hw/todo-list.txt")
        channel.close()

    def test_retr_recursive(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("RETR", "/documents/homeworks/xxx.txt", "other-hw/retr.txt")
        channel.close()

    def test_list_dir_not_exist(self):
        channel = ControlChannel(hostname, control_channel_port, username, password)
        channel.issue_service_cmd("LIST", "/documents/homeworks")
        channel.close()


if __name__ == '__main__':
    unittest.main()
