
import argparse
import socket
import ssl

# parse arguments using argparse
parser = argparse.ArgumentParser(description='Process mathematical expressions')

# specify command-line argument options accepted 
parser.add_argument('host', type=str)
parser.add_argument('neuId', type=str)
parser.add_argument('-p', type=int, dest='port')
parser.add_argument('-s', action='store_true', dest='ssl', default=False)

args = parser.parse_args()

HOST = args.host
NEU_ID = args.neuId
PORT = args.port
SSL = args.ssl

# check if the port or ssl flag is given to change the port number 
if PORT is None:
    if not SSL:
        PORT = 27997
    else:
        PORT = 27998

BUFF_SIZE = 16384
HELLO = 'cs5700spring2021 HELLO {}\n'.format(NEU_ID)

# receive all the messages from server until EOF
def recv_all(s_client):
    res = ''
    # keep reading from server until reading "\n"
    while True:
        res += s_client.recv(BUFF_SIZE).decode('ascii')
        if res.endswith('\n'):
            return res

# keep receive and send messages between server and client until receive 'BYE'
def event_loop(s_client):
    s_client.connect(address)
    s_client.send(HELLO.encode('ascii'))
    while True:
        msg = recv_all(s_client)
        msg_list = msg.split(' ', 2)
        msg_type = msg_list[1]
        if msg_type == 'EVAL':
            txpr = msg_list[2].rstrip()
            try:
                solution = eval(txpr)
                s_client.send('cs5700spring2021 STATUS {}\n'.format(solution).encode())
            except ZeroDivisionError:
                s_client.send(b'cs5700spring2021 ERR #DIV/0\n')
        elif msg_type == 'BYE':
            secret = msg_list[2]
            print(secret)
            break
        else:
            exit("Wrong Message Type!")
            

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (HOST, PORT)

if SSL:
    # connect to server using an encrypted SSL socket 
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ssl_client = context.wrap_socket(client)
    event_loop(ssl_client)
    ssl_client.close()
else:
    # normal socket
    event_loop(client)
client.close()

