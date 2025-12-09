#!/bin/bash

INTERFACE="wlan0"
SSID=$(iwctl station $INTERFACE show | awk '/Connected network/ { $1=""; $2=""; gsub(/^[ \t]+/, ""); print }')

if [ -n "$SSID" ]; then
    if ping -c 1 -W 1 8.8.8.8 &> /dev/null; then
	STATUS="Internet"
    else
	STATUS="No internet"
	sudo dhclient $INTERFACE &> /dev/null
	sleep 2
    fi
else
    SSID=" - "
fi

echo "$SSID"