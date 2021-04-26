import socket
import logging
import os

BUFFER_SIZE = 1014


def parse_pasv_message(message):
    _, m = message.rsplit(" ", 1)
    nums = m.strip()[1: -2].split(",")
    ip = ".".join(nums[:4])
    port = int(nums[4]) * 256 + int(nums[5])
    return ip, port


def parse_message(response):
    code, m = response.split(" ", 1)
    return code, m


def is_data_channel_required(cmd):
    return cmd not in ["MKD", "RMD", "DELE"]


class Channel:
    def __init__(self, hostname, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((hostname, port))
        self.logger = logging.getLogger(self.__class__.__name__)

    def receive_all(self):
        data = ''
        while True:
            buffer = self.s.recv(BUFFER_SIZE)
            b = buffer.decode('ascii')
            data += b
            if not b or len(buffer) < BUFFER_SIZE:
                break

        self.logger.debug(data.strip())
        return data

    def write(self, content):
        self.logger.debug(content)
        data = (content + '\n').encode('ascii')
        self.s.sendall(data)

    def write_file(self, file):
        data = file.read(BUFFER_SIZE)
        while data:
            self.s.send(data)
            data = file.read(BUFFER_SIZE)

    def read_file(self, file):
        recv_data = self.s.recv(BUFFER_SIZE)
        while recv_data:
            file.write(recv_data)
            recv_data = self.s.recv(BUFFER_SIZE)

    def close(self):
        self.s.close()


class ControlChannel(Channel):
    def __init__(self, hostname, port, username, password):
        Channel.__init__(self, hostname, port)
        self.receive_all()
        commands = ["USER " + username, "PASS " + password, "TYPE I", "MODE S", "STRU F"]
        for c in commands:
            self.write(c)
            r = self.receive_all()
            code, _ = parse_message(r)
            # if not code.startswith("2"):
            #     raise Exception("Service Command Failed")

    def receive_all(self):
        message = Channel.receive_all(self)
        code, _ = parse_message(message)
        if code.startswith('4') or code.startswith('5'):
            raise Exception('Command execution failure')
        return message

    def create_dir(self, directory):
        dir = '/'
        for folder in directory.split('/')[1:]:
            dir += folder
            dir += '/'
            if dir == '/':
                continue
            self.write("MKD " + dir)
            try:
                self.receive_all()
            except:
                continue

    def issue_service_cmd(self, cmd, path, local_path=None):
        if cmd == 'MKD':
            self.create_dir(path)
            return
        if not is_data_channel_required(cmd):
            self.write(cmd + " " + path)
            self.receive_all()
            return
        data_channel = self.start_data_channel()
        if cmd == "LIST":
            self.write(cmd + " " + path)
            self.receive_all()
            message = data_channel.receive_all()
            print(message)
            self.receive_all()
            data_channel.close()
        elif cmd == "STOR":
            directory = os.path.dirname(path)
            self.create_dir(directory)
            self.write(cmd + " " + path)
            self.receive_all()
            with open(local_path, 'rb') as f:
                data_channel.write_file(f)
            data_channel.close()
            self.receive_all()
        elif cmd == "RETR":
            self.write(cmd + " " + path)
            self.receive_all()
            if os.path.dirname(local_path):
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                data_channel.read_file(f)
            self.receive_all()

    def start_data_channel(self):
        self.write("PASV")
        response = self.receive_all()
        code, message = parse_message(response)
        if code != "227":
            raise Exception("PASV command failed.")
        ip, port = parse_pasv_message(message)
        return Channel(ip, port)

    def close(self):
        self.write('QUIT')
        Channel.close(self)
