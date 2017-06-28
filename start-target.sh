#!/bin/bash
sudo ip link set up dev eth0
sudo ip addr add 192.168.0.1/30 dev eth0
# sudo ./debug_client.py ./config/debug_client.config
./debug_client.py ./config/debug_client.config
