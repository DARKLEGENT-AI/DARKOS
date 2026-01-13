#!/bin/bash

IFACE="wlp3s0"

# Получаем SSID активного подключения на нужном интерфейсе
SSID=$(nmcli -t -f NAME,DEVICE connection show --active | grep "${IFACE}$" | cut -d: -f1)

if [ -n "$SSID" ]; then
    # Проверяем доступ в интернет
    if [ "$(nmcli -t -f CONNECTIVITY general)" = "full" ]; then
        STATUS="Internet"
    else
        STATUS="No internet"
        echo "Интернета нет, переподключаем $IFACE..."
        nmcli device disconnect "$IFACE" >/dev/null 2>&1
        sleep 2
        nmcli device connect "$IFACE" >/dev/null 2>&1
    fi
else
    SSID=" - "
    STATUS="Disconnected"
fi

echo "$SSID"