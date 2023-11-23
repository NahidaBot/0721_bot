#!/bin/bash
DIR=$(pwd)
name = nenebot.service
systemd_service=/etc/systemd/system/$name

echo "installing pip requirements"
pip3 install -r requirements.txt

echo "installing service"
cat >$systemd_service << EOF
[Unit]
Description=Nahida Picbot for telegram channel
After=network.target

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 bot.py
Restart=always
EOF
chmod +x $systemd_service

echo "service starting"
systemctl enable --now $name
systemctl status $name