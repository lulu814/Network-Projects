# Project 4: Raw Sockets

Implementation of HTTP GET with low-level operations of the Internet protocol stack.

## Team
- Lu Liu - HTTP and TCP/IP header generation/parsing
- Tuo Liu - TCP IP socket implementation

## Usage
```
usage: ./rawhttpget [url]
```

## Environment setup
It disables RST drop and TCP segment offloading, maybe not requried on test servers.
```
sudo ./start.sh
```

## High Level Design
1. Use python raw socket to implement from network layer
2. Use socket IPPROTO_RAW for send, and IPPROTO_TCP for receive
3. Generate/parse the TCP, IP, HTTP headers and payloads.
4. Impement checksum generation/checking and TCP logics to handle out of order packets, congestion control and retransmission.

## Implementation Details
1. IpPacket and TcpSegment class to represent the header and payload for each layer.
    - fillin correct Tcp checksum derived from pseduo ip header + tcp packet when generate tcp segment bytes
    - fill in other relevant information in ip and tcp header
2. SendSocket and RecvSocket to represent the Network layer socket, which handles parse to/from btyes, IP header checksum validation and timeout if nothing filtered in timeout time.
    - checksum function validate if header checksum is 0
    - filter packets with desired source and destination address
    - break the loop and return none if no desired packet received within timeout
    - return IpPacket instance if desired packet is received
3. TcpSocket to represent the transport layer socket, which handles TCP handshake, teardown, send/receive with congestion control, retransmission and timeout
    - TCP handshake with server at the beginning. If three minutes elapsed with no reply from server, throw exception so caller function can exit
    - Tcp teardown when segment with FIN flag received from server or client initiate teardown.
    - Send data is sliced to multiple chuncks based on segment size, use congestion control window (cwnd) to control the send buffer size.
    - Timeout of 1 minute for acks, if no ack within 1 minute retransmit packets in send buffer. If acked, acked packets are removed from send buffer.
    - Congestion control window start from 1, each acked packets the congestion control window increases by 1. If timeout occured. the congestion window is reset to 1. The congestion control window is limit to 1000.
    - The received packets are put into non-acked buffer, all in-order packets are cleared from non-acked buffer, and ack no is incremented and ack is sent to server.
    - If received packet's sequence number is less than current ack number, it is ignored.
    - If received packet's sequence number is larger than current ack number, it is placed in non-acked buffer and ack with current ack number is sent to server
    - When the last acked packet has a FIN flag, initiate teardown.
4. Raw Http Get to generate http headers and data, send to server and receive data from server.
    - Use http 1.0 such that server initiate teardown when all data is sent
    - Use bytes processing so the data session of HTTP response can be binary data.
    - Use filename index.html if path portion of url is empty or end with slash, otherwise use the name in path portion

## Challenges
1. The checksum for large packets is not correct for my environment if TCP segmentation offloading option is on. High checksum error will halt the transmission eventually.
2. Building headers from scratch is error prone and hard to debug.
3. Packets are not acked by server if checksum is incorrect, it is hard to tell what causes the no response.
