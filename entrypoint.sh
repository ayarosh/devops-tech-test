#!/bin/bash
# add additional dependencies required for your solution here.
# for example:
# pip3 install mysql-client
# sleep infinity

pip3 install -r /scripts/requirements.txt
python3 /scripts/update.py
