#!/bin/bash
sudo ip link set up dev eth0
sudo ./debug_client.py ./config/debug_client.config
