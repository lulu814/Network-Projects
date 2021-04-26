import socket
import logging


from datetime import timedelta, datetime
from utils import *


class SendSocket:
    def __init__(self, source_ip, destination_ip, destination_port=80):
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.packet_id = 0
        self.logger = logging.getLogger(self.__class__.__name__)

    def send(self, data):
        ip_packet = IpPacket(self.packet_id, self.source_ip,
                             self.destination_ip, payload=data)
        self.packet_id = (1 + self.packet_id) % 65536
        self.socket.sendto(
            ip_packet.to_bytes(), (self.destination_ip, self.destination_port))

    def close(self):
        self.socket.close()


class RecvSocket:
    def __init__(self, source_ip, destination_ip, buffer_size=65535, timeout=4):
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket.settimeout(timeout)
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def recv(self, wait_until):
        try:
            while True:
                # timeout
                if wait_until < datetime.now():
                    return
                data = self.socket.recv(self.buffer_size)
                ip_header_data = data[:20]
                ip_packet = IpPacket.from_bytes(data)

                # filter packets not from correct
                if ip_packet.source_ip != self.source_ip or ip_packet.dest_ip != self.destination_ip:
                    continue
                if calculate_checksum(ip_header_data) != 0:
                    self.logger.debug('Corrupted ip packet received and droped.')
                    continue
                return ip_packet.payload
        except socket.timeout:
            # timeout
            return

    def close(self):
        self.socket.close()
