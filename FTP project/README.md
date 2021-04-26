# Project: FTP Client
An implementation of commandline FTP client


## Installation

No installation is needed, all libraries used are pre-installed on khoury linux machine.

## Usage
usage: ftp_client.py [-h] [--verbose] operation params [params ...]

## Design
The project contains three main parts, the commandline parser, issue command to ftp server and channel implementation.

### Commandline parser
The command line parser is implemented using argparse library. By setting up the positional arguments and optional arguments such as --verbose, we obtained operations and the given file urls from the command line arguments. Valid operations are 'ls', 'rm', 'rmdir','mkdir', 'cp', and 'mv', and there will be one or two paths but it must include one remote ftp url. The parsed operations and file paths will be passed to control channel for command execution to ftp server (and local server).
 
### Issue service command
For operations 'ls', 'rm', 'rmdir' and 'mkdir', the control channel will issue service command of 'LIST', 'DELE', 'RMD', 'MKD' respectively to ftp server. 

For operations 'cp' and 'mv', the issue service command will have to work on both local files and remote files. For 'cp', if the first argument after 'cp' is local file, it will issue 'STOR' command to copy the local file to the ftp server path (the second argument), otherwise, it will issue 'RETR' command to copy the remote file from ftp server to local path; for 'mv', if the first argument after 'mv' is local file, it will first issue 'STOR' command to copy the local file to ftp server and then delete the local file, otherwise, it will first issue 'RETR' command to copy the remote file from ftp server to local path and then issue 'DELE' command to delete the remote file from ftp server

### Data channel and Control channel
Both channel use a base class channel, which takes in hostname and port to establish a TCP socket connection to server.
The base channel class can send bytes to server and read bytes from server.

For Data channel, it just use the base channel class. The data channel is used when FTP needs to receive or send data to FTP server.
For example, copy local file to remote server will write file bytes to ftp server.

For Control channel, it is used to issue service command to FTP server. In the constructor function, username and password are taken as extra input.
The channel uses authentication information to communicate with FTP server and get authenticated. Several other service commands are issued after authenticated to setup communication mode.

When issuing commands like DELE, MKD, RMD, data channel is not required.
For commands like LIST, data channel is required. We issue PASV command through control channel first to let FTP server open a random port for us to use as data channel.
The PASV response looks like `227 Entering Passive Mode (129,10,111,152,4,159)`, in the parentheses, the first 4 numbers are IP address, the last 2 numbers are port number. The port number is 256 * n1 + n2.

After we parse the IP and port for data channel, then we can open a data channel to either write to server or receive from server. For writing, the client closes the connection when finish. For receiving, the server closes the connection.

## Testing
- unit test for channel and other helper functions.