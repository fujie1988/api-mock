#!/usr/bin/env bash

echo "***************************"
echo "setup start"
echo "***************************"

mkdir venv
python3 -m venv ./venv
source ./venv/bin/activate
pip3 install -r ./requirements.txt
