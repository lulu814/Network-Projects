#!/bin/bash
sudo ethtool -K eth0 tso off gso off gro off
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP