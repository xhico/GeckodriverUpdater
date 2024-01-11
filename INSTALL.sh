#!/bin/bash

sudo mv /home/pi/GeckodriverUpdater/GeckodriverUpdater.service /etc/systemd/system/ && sudo systemctl daemon-reload
python3 -m pip install -r /home/pi/GeckodriverUpdater/requirements.txt --no-cache-dir
chmod +x -R /home/pi/GeckodriverUpdater/*