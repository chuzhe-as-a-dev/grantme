#!/bin/bash

if [ ! -d "/var/lib/grant" ]; then
    mkdir "/var/lib/grant"
fi
if [ ! -d "/var/lib/grant/shared" ]; then
    mkdir "/var/lib/grant/shared"
fi
if [ ! -d "/var/lib/grant/exclusive" ]; then
    mkdir "/var/lib/grant/exclusive"
fi

chmod o+x "/var/lib/grant"
chmod o+w "/var/lib/grant/shared"
chmod o+w "/var/lib/grant/exclusive"
chmod +t "/var/lib/grant/shared"
chmod +t "/var/lib/grant/exclusive"

ln grantme /usr/local/bin/grantme
cp 51-grantme-status /etc/update-motd.d/51-grantme-status

chmod +x /usr/local/bin/grantme
chmod +x /etc/update-motd.d/51-grantme-status