#!/bin/bash

DEFAULT_IFACE="wg0"

if [[ "$1" == "choose" ]]; then
    FILE=$(zenity --file-selection \
        --title="Выберите конфиг WireGuard" \
        --file-filter="*.conf")

    [[ -z "$FILE" ]] && exit 1

    CONF="$FILE"
    IFACE=$(basename "$CONF" .conf)
else
    CONF="$DEFAULT_IFACE"
    IFACE="$DEFAULT_IFACE"
fi

if ip link show "$IFACE" &>/dev/null; then
    sudo wg-quick down "$CONF"
else
    sudo wg-quick up "$CONF"
fi
