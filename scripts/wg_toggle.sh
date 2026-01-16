#!/bin/bash

DEFAULT_IFACE="wg0"
LOADING_FILE="$HOME/.cache/wg_loading"

mkdir -p "$HOME/.cache"
touch "$LOADING_FILE"

# Чтобы файл точно удалился даже при ошибке
trap 'rm -f "$LOADING_FILE"; polybar-msg hook vpn 1' EXIT

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
