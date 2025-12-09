#!/bin/bash
INTERFACE="wlan0"

SSID=$(iwctl station $INTERFACE get-networks | tail -n +2 | awk '{$1=""; gsub(/^[ \t]+\, ""); print}' | rofi -dmenu -i -p "Select Wi-Fi")

if [ -n "$SSID" ]; then
    PASSWORD=$(rofi -dmenu -p "Password for $SSID")
    echo -e "$PASSWORD" | iwctl station $INTERFACE connect "$SSID"
fi 