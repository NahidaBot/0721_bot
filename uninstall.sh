#!/bin/bash
name = nenebot.service
systemd_service=/etc/systemd/system/$name

echo "service stopping"
systemctl disable --now $name

echo "removing service"
rm -v $systemd_service

echo "Please remove pip packages manually, because other python programs may depend on these packages."