from tcp_socket import TcpSocket
import logging

request = """\
GET /static/rawhttp/10MB.log HTTP/1.0
Host: webcrawler-site.ccs.neu.edu
Accept: text/html\n
""".encode('ascii')

# request = """\
# GET / HTTP/1.0
# Host: webcrawler-site.ccs.neu.edu
# Accept: text/html\n
# """.encode('ascii')

logging.basicConfig(level=logging.DEBUG)
s = TcpSocket("webcrawler-site.ccs.neu.edu")
s.connect()
s.send(request)
response = s.recv()
s.close()