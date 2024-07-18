#!/bin/bash

python run_server.py &
python run_client.py --config ./client_1.yaml &
python run_client.py --config ./client_2.yaml &
wait