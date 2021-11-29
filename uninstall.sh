#!/bin/bash

rm -rf \
    /var/lib/grant \
    /var/lib/grant/shared \
    /var/lib/grant/exclusive \
    /usr/local/bin/grantme \
    /etc/update-motd.d/51-grantme-status
