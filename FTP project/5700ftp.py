import argparse
import logging
from urllib.parse import urlparse
from channel import ControlChannel
import os

DEFAULT_FTP_PORT = 21
DEFAULT_USER = 'anonymous'

# Part 1: setup argparse arguments

parser = argparse.ArgumentParser(
    description='''
    FTP client for listing, copying, moving, and deleting files and directories on remote FTP servers.

    positional arguments:
    operation      The operation to execute. Valid operations are 'ls', 'rm', 'rmdir',
    'mkdir', 'cp', and 'mv'
    params         Parameters for the given operation. Will be one or two paths and/or URLs.
    '''
)
parser.add_argument('--verbose',  '-v',  help='Print all messages to and from the FTP server', action='store_true')
parser.add_argument('operation', help='Operation')
parser.add_argument('params', type=str, nargs='+', help='Parameters')
args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)


# Part 2: parse the key params

arg1_o = urlparse(args.params[0])

# get the remote file and local file (if exists)
ftp_url = None
local_file = None

if arg1_o.scheme == 'ftp':
    ftp_url = arg1_o
    if len(args.params) == 2:
        local_file = args.params[1]
elif len(args.params) != 2:
    logging.error("Illegal arguments")
    exit(1)
else:
    local_file = args.params[0]
    ftp_url = urlparse(args.params[1])

hostname = ftp_url.hostname
username = ftp_url.username or DEFAULT_USER
password = ftp_url.password or ''
port = ftp_url.port or DEFAULT_FTP_PORT

if not hostname:
    logging.error("Host is not specified in url.")
    exit(1)


# Part 3: execute commands using the control_channel object

control_channel = ControlChannel(hostname, port, username, password)

try:
    if args.operation == 'ls':
        control_channel.issue_service_cmd("LIST", ftp_url.path)
    elif args.operation == 'rm':
        control_channel.issue_service_cmd("DELE", ftp_url.path)
    elif args.operation == 'rmdir':
        control_channel.issue_service_cmd("RMD", ftp_url.path)
    elif args.operation == 'mkdir':
        control_channel.issue_service_cmd("MKD", ftp_url.path)
    elif args.operation == 'cp' and local_file:
        if ftp_url == arg1_o:
            control_channel.issue_service_cmd("RETR", ftp_url.path, local_file)
        else:
            control_channel.issue_service_cmd("STOR", ftp_url.path, local_file)
    elif args.operation == 'mv' and local_file:
        if ftp_url == arg1_o:
            control_channel.issue_service_cmd("RETR", ftp_url.path, local_file)
            control_channel.issue_service_cmd("DELE", ftp_url.path)
        else:
            control_channel.issue_service_cmd("STOR", ftp_url.path, local_file)
            os.remove(local_file)
    else:
        logging.error("Unknown command.")
        exit(1)
    control_channel.close()
except Exception:
    logging.error('Fail to execute command')
    exit(1)

