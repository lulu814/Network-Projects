from raw_socket import SendSocket, RecvSocket
from utils import *
from random import randint
import logging
from datetime import timedelta, datetime


class TcpSocket:
    def __init__(self, hostname):
        self.is_connected = False
        self.source_ip = get_local_ip()
        self.dest_ip = get_remote_ip(hostname)
        self.source_port = int(get_free_port())
        self.dest_port = 80
        self.send_socket = SendSocket(
            self.source_ip, self.dest_ip, self.dest_port)
        self.recv_socket = RecvSocket(self.dest_ip, self.source_ip)
        self.seq_no = randint(0, (2 << 31) - 1)
        self.ack_no = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        # congestion control
        self.cwnd = 1
        # receiver window
        self.rwnd = 1
        # send buffer
        self.send_buffer = dict()
        # receive buffer
        self.recv_buffer = b''
        # not acked buffer
        self.non_acked = dict()
        self.last_processed_packet = None

    # three way handshake

    def connect(self):
        # send syn
        self._send(get_tcp_flags(syn=1))

        # wait three minutes for connection, if nothing returned, raise exception
        wait_until = datetime.now() + timedelta(seconds=180)
        tcp_seg = self._recv(wait_until)
        if not tcp_seg or tcp_seg.flags != get_tcp_flags(syn=1, ack=1):
            raise RuntimeError('TCP handshake failed.')
        self.seq_no = tcp_seg.ack_no
        # syn flag is equavalent to 1 byte data
        self.ack_no = tcp_seg.seq_no + 1
        self._send(get_tcp_flags(ack=1))
        self.is_connected = True
        self.logger.debug('Connection started.')

    def _send(self, flags, payload=b''):
        tcp_segment = TcpSegment(
            self.source_port, self.dest_port, self.seq_no, self.ack_no, flags, payload=payload)
        self.send_socket.send(tcp_segment.to_bytes(
            self.source_ip, self.dest_ip))

    def _recv(self, wait_until=None):
        # default timeout 60 seconds
        if not wait_until:
            wait_until = datetime.now() + timedelta(seconds=60)
        data = self.recv_socket.recv(wait_until)
        if data is None:
            return
        # validate checksum, skip if not valid
        pseudo_ip_header = get_pseudo_ip_header(
            self.dest_ip, self.source_ip, len(data))
        if calculate_checksum(pseudo_ip_header + data) != 0:
            self.logger.debug('TCP packet is corrupted, skip.')
            return self._recv(wait_until)
        return TcpSegment.from_bytes(data)

    def close(self):
        if self.is_connected:
            self._teardown()
        self.send_socket.close()
        self.recv_socket.close()
        self.logger.debug('Connection closed.')

    def _teardown(self):
        # send fin ack
        self.logger.debug('teardown starts')
        self._send(get_tcp_flags(fin=1, ack=1))
        tcp_seg = self._recv()
        if not tcp_seg or tcp_seg.flags & get_tcp_flags(ack=1) == 0:
            raise Exception('TCP teardown failed, no fin ack received.')
        self.seq_no = tcp_seg.ack_no
        self.ack_no = tcp_seg.seq_no + 1
        if tcp_seg.flags & get_tcp_flags(fin=1):
            self._send(get_tcp_flags(ack=1))
        self.is_connected = False

    def send(self, data):
        # psh and ack
        flags = get_tcp_flags(psh=1, ack=1)
        # slice the data to mutiple chunks
        data_chuncks = slice_data(self.seq_no, data)
        while data_chuncks:
            for i in range(self.cwnd):
                seq, chunck = data_chuncks.popleft()
                tcp_segment = TcpSegment(
                    self.source_port, self.dest_port, seq, self.ack_no, flags, payload=chunck)
                tcp_seg_bytes = tcp_segment.to_bytes(
                    self.source_ip, self.dest_ip)
                self.send_buffer[tcp_segment.seq_no] = tcp_seg_bytes
                self.send_socket.send(tcp_seg_bytes)
            self._recv_ack()
        assert len(self.send_buffer) == 0
        return

    def _recv_ack(self):
        ack_seg = self._recv()
        if not ack_seg:
            # timeout happens after 60 seconds
            self.cwnd = 1
            # resend or unacked packets
            for tcp_seg_bytes in self.send_buffer:
                self.send_socket.send(tcp_seg_bytes)
            return
        # all sequence number less than ack no is acked
        for seq in sorted(self.send_buffer.keys()):
            if seq < ack_seg.ack_no:
                del self.send_buffer[seq]
        self.seq_no = ack_seg.ack_no

    def recv(self):
        data = b''
        while True:
            tcp_segment = self._recv()
            if not tcp_segment:
                # timeout happens
                self.logger.debug('Timeout happened.')
                self.cwnd = 1
                continue

            self.logger.debug('Cur Ack: {}, received packet seq: {}'.format(self.ack_no, tcp_segment.seq_no))
            if tcp_segment.flags & get_tcp_flags(ack=1):
                self.cwnd += 1
                self.cwnd = min(self.cwnd, 1000)
            if tcp_segment.seq_no > self.ack_no:
                self.non_acked[tcp_segment.seq_no] = tcp_segment
                self.logger.debug('out of order packet received with seq {}, greater than cur ack no.'.format(tcp_segment.seq_no))
                self._send(get_tcp_flags(ack=1))
            elif tcp_segment.seq_no < self.ack_no:
                self.logger.debug('out of order packet received with seq {}, less than cur ack no.'.format(tcp_segment.seq_no))
                # self._send(get_tcp_flags(ack=1))
            else:
                self.non_acked[tcp_segment.seq_no] = tcp_segment
                data = self._clear_recv_buffer(data)
            self.logger.debug('received data of length {}'.format(
                len(tcp_segment.payload)))
            if self.last_processed_packet and self.last_processed_packet.flags & get_tcp_flags(fin=1):
                self.logger.debug('Last processed packet with seq {} has fin flag.'.format(self.last_processed_packet.seq_no))
                break
        return data

    def _clear_recv_buffer(self, data):
        for seq in sorted(self.non_acked.keys()):
            if self.ack_no == seq:
                next_chunck = self.non_acked[seq]
                self.ack_no += len(next_chunck.payload)
                data += next_chunck.payload
                self.seq_no = max(self.seq_no, next_chunck.ack_no)
                del self.non_acked[seq]
                self.logger.debug('cleared segment {}'.format(seq))
                self.last_processed_packet = next_chunck
            else:
                break
        # send ack
        if self.last_processed_packet.flags & get_tcp_flags(fin=1):
            # fin flag is equavalent to 1 byte data
            self.ack_no += 1
            self._teardown()
        else:
            self._send(get_tcp_flags(ack=1))
        # write to data
        return data
