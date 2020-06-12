#!/bin/bash
sudo ip link set up dev vmnet8
sudo ./debug_client.py config/debug_client_vmware.config
