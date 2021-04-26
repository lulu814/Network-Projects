import socket
from struct import pack, unpack
import array
from collections import deque


IP_HEADER_FORMAT = '!BBHHHBBH4s4s'
TCP_HEADER_FORMAT = '!HHLLBBHHH'
SEGMENT_SIZE = 1460  # bytes
BUFFER_SIZE = 262144


def slice_data(start_seq_no, data):
    data_chuncks = [data[i:min(i + SEGMENT_SIZE, len(data))]
                    for i in range(0, len(data), SEGMENT_SIZE)]
    dq = deque()
    seq = start_seq_no
    for chunck in data_chuncks:
        dq.append((seq, chunck))
        seq += len(chunck)
    return dq


# resolve remote host ip address
def get_remote_ip(hostname):
    return socket.gethostbyname(hostname)


# use google dns to get local ip address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # google dns
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr = s.getsockname()
    s.close()
    return addr[1]


def calculate_checksum(packet):
    cks = 0
    if len(packet) % 2 != 0:
        packet += b'\0'
    for i in range(0, len(packet), 2):
        w = (packet[i] << 8) + (packet[i+1])
        cks += w

    cks = (cks >> 16) + (cks & 0xffff)
    cks = ~cks & 0xffff

    return cks


def get_tcp_flags(fin=0, syn=0, rst=0, psh=0, ack=0, urg=0):
    return fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)


def get_pseudo_ip_header(source_ip, dest_ip, tcp_length):
    source_address = socket.inet_aton(source_ip)
    dest_address = socket.inet_aton(dest_ip)
    protocol = socket.IPPROTO_TCP
    pseudo_ip_header = pack('!4s4sHH', source_address,
                            dest_address, protocol, tcp_length)
    return pseudo_ip_header


class IpPacket:
    def __init__(self, identification, source_ip, dest_ip, payload, version=4, ihl=5, type_of_service=0, total_length=0, flags_and_fragment_offset=0, time_to_live=64, protocol=socket.IPPROTO_TCP):
        self.source_ip = source_ip
        self.identification = identification
        self.dest_ip = dest_ip
        self.version = version
        self.ihl = ihl
        self.type_of_service = type_of_service
        self.total_length = total_length
        self.flags_and_fragment_offset = flags_and_fragment_offset
        self.time_to_live = time_to_live
        self.protocol = protocol
        # filled by kernel
        self.header_checksum = 0
        self.payload = payload

    @classmethod
    def from_bytes(cls, data):
        version_and_ihl, type_of_service, total_length, identification, flags_and_fragment_offset, time_to_live, protocol, header_checksum, source_address, destination_address = unpack(
            IP_HEADER_FORMAT, data[:20])
        source_ip = socket.inet_ntoa(source_address)
        dest_ip = socket.inet_ntoa(destination_address)
        version = version_and_ihl >> 4
        ihl = version_and_ihl & (1 << 5 - 1)
        instance = cls(identification, source_ip, dest_ip,
                       data[20:], version, ihl, type_of_service, total_length, flags_and_fragment_offset, time_to_live, protocol)
        instance.header_checksum = header_checksum
        return instance

    def to_bytes(self):
        source_address = socket.inet_aton(self.source_ip)
        destination_address = socket.inet_aton(self.dest_ip)
        header = pack(
            IP_HEADER_FORMAT,
            (self.version << 4) + self.ihl,
            self.type_of_service,
            self.total_length,
            self.identification,
            self.flags_and_fragment_offset,
            self.time_to_live,
            self.protocol,
            self.header_checksum,
            source_address,
            destination_address
        )
        return header + self.payload


class TcpSegment:
    def __init__(self, source_port, dest_port, seq_no, ack_no, flags, data_offset=5, window=64240, urgent_pointer=0, payload=b''):
        self.source_port = source_port
        self.dest_port = dest_port
        self.seq_no = seq_no
        self.ack_no = ack_no
        self.flags = flags
        self.payload = payload
        self.data_offset = data_offset
        self.window = window
        self.urgent_pointer = urgent_pointer

    @classmethod
    def from_bytes(cls, data):
        source_port, dest_port, seq_no, ack_no, offset_and_reserved, flags, window, checksum, urgent_pointer = unpack(
            TCP_HEADER_FORMAT, data[:20])
        data_offset = offset_and_reserved >> 4
        window = socket.ntohs(window)
        payload = data[data_offset * 4:]
        instance = cls(source_port, dest_port, seq_no, ack_no,
                       flags, data_offset, window, 0, payload)
        return instance

    def to_bytes(self, source_ip, dest_ip):
        window = socket.htons(self.window)
        # initialize checksum as 0
        checksum = 0

        offset_and_reserved = self.data_offset << 4

        data_withoutchecksum = pack(
            TCP_HEADER_FORMAT,
            self.source_port,
            self.dest_port,
            self.seq_no,
            self.ack_no,
            offset_and_reserved,
            self.flags,
            window,
            checksum,
            self.urgent_pointer
        ) + self.payload

        # generate pseudo ip header
        pseudo_ip_header = get_pseudo_ip_header(
            source_ip, dest_ip, len(data_withoutchecksum))
        checksum = calculate_checksum(
            pseudo_ip_header + data_withoutchecksum)
        header = pack(
            TCP_HEADER_FORMAT,
            self.source_port,
            self.dest_port,
            self.seq_no,
            self.ack_no,
            offset_and_reserved,
            self.flags,
            window,
            checksum,
            self.urgent_pointer
        )
        return header + self.payload
