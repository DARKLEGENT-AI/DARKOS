#!/bin/bash

LOADING_FILE="$HOME/.cache/wg_loading"

# Если идёт загрузка
if [[ -f "$LOADING_FILE" ]]; then
    echo "%{F#fbc02d}󰑓 VPN Загружается%{F-}"  # значок загрузки
    exit 0
fi

IFACE=$(wg show interfaces)

if [[ -n "$IFACE" ]]; then
    echo "%{F#7cb342}󰌾 VPN ON ($IFACE)%{F-}"
else
    echo "%{F#A54242}󰌿 VPN OFF%{F-}"
fi
