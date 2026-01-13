#!/bin/bash

IFACE=$(wg show interfaces)

if [[ -n "$IFACE" ]]; then
    echo "%{F#7cb342}VPN ON ($IFACE)%{F-}"
else
    echo "%{F#A54242}VPN OFF%{F-}"
fi
