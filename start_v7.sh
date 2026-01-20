#!/bin/bash

source ~/.bashrc

nohup python3 /home/ubuntu/gemini_code/gemini_server_v7.py --port 8080 > server.log 2>&1 &