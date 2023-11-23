#!/bin/bash
DIR=$(pwd)
name=nenebot.service
systemd_service=/etc/systemd/system/$name

echo "installing pip requirements..."
pip3 install -r requirements.txt

echo "installing service..."
cat >$systemd_service << EOF
[Unit]
Description=0721 Bot (* /ω＼*)
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

echo "copying configure file.."
cp .env.example .env

echo "Please input your telegram bot token: "
read bot_token
sed -i "s/bot_token_here/$bot_token/" ./.env

echo "service starting"
systemctl enable --now $name
systemctl status $name