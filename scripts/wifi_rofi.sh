#!/bin/bash

exec 2>/tmp/debug_wifi.txt

# Обновляем список
nmcli dev wifi rescan >/dev/null 2>&1

# SSID + SECURITY + SIGNAL, без пустых и --
wifi_list=$(nmcli -t -f SSID,SECURITY,SIGNAL dev wifi list \
  | awk -F: '$1!="" {printf "%s  [%s]  (%s%%)\n",$1,($2=="--"?"open":$2),$3}' \
  | sort -u)

[ -z "$wifi_list" ] && echo "No networks" | rofi -dmenu -p WiFi && exit 0

chosen=$(echo "$wifi_list" | rofi -dmenu -p WiFi -theme /usr/share/rofi/themes/DARKOS.RASI)
[ -z "$chosen" ] && exit 0

# SSID
ssid=$(echo "$chosen" | sed 's/  \[.*//')

# SECURITY из NM (не из меню)
security=$(nmcli -t -f SECURITY dev wifi list | awk -F: -v s="$ssid" '$0~("^"s":"){print $2; exit}')

# Открытая сеть
if [ -z "$security" ] || [ "$security" = "--" ]; then
    nmcli dev wifi connect "$ssid"
    exit 0
fi

# Пароль
password=$(rofi -dmenu -password -p "Password: $ssid")
[ -z "$password" ] && exit 0

nmcli dev wifi connect "$ssid" password "$password"
