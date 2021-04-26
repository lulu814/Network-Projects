import sys
import re

from tcp_socket import TcpSocket
from urllib.parse import urlparse
from utils import *


def parse_response(response):
    status_line, response = response.split(b'\r\n', 1)
    status_line = status_line.decode('ascii')
    version, code, reason_phrase = status_line.split(" ", 2)
    headers, content = response.split(b'\r\n\r\n', 1)
    headers = headers.decode('ascii')
    cookies = dict()
    parsed_headers = dict()
    for h in headers.split('\r\n'):
        key, value = h.split(': ', 1)
        if key == 'Set-Cookie':
            c = value.split("; ", 1)[0]
            cookie_key, cookie_value = c.split("=", 1)
            cookies[cookie_key] = cookie_value
        else:
            parsed_headers[key] = value
    return code, reason_phrase, content, cookies, parsed_headers


def send_request(request, hostname):
    s = TcpSocket(hostname)
    s.connect()
    s.send(request)
    buffer = s.recv()
    response = buffer
    s.close()
    return response


def get(path, hostname, filename):
    get_header = """\
GET {} HTTP/1.0
Host: {}
Accept: text/html\n
"""
    request = get_header.format(path, hostname).encode('ascii')
    try:
        response = send_request(request, hostname)
    except RuntimeError:
        print('Cannot connect to server')
        exit(0)
    code, reason, content, _, headers = parse_response(response)

    if code == '200':
        with open(filename, 'wb') as file:
            file.write(content)
            return
    else:
        print('Status code is not correct: {}'.format(code), file=sys.stderr)


# check arguments
if len(sys.argv) != 2:
    print("usage: ./rawhttpget [url]", file=sys.stderr)
    exit(128)

url = sys.argv[1]

o = urlparse(url)
hostname = o.hostname
path = o.path
if path.endswith('/') or o.path == '':
    filename = 'index.html'
else:
    filename = path.split('/')[-1]
get(path, hostname, filename)
