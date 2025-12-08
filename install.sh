#!/usr/bin/env bash
set -e

log() { echo -e "\n=== $1 ===\n"; }

### --- Пакеты --- ###
install_pkgs() {
    log "Установка основных пакетов Debain"
    sudo apt update
    sudo apt install -y \
        bspwm sxhkd polybar rofi nitrogen picom \
        network-manager pulseaudio pavucontrol \
        bluez blueman xinput xbacklight \
        git curl unzip \
        firmware-misc-nonfree intel-media-va-driver-non-free \
        dolphin
    log "Установка доп пакетов"
    sudo apt install -y \
        telegram-desktop firefox-esr code thunderberd libreoffice \
        chromium
}

### --- Копирование конфигов --- ###
install_configs() {
    log "Копирование конфигов"

    mkdir -p ~/.config/bspwm ~/.config/sxhkd ~/.config/polybar

    cp -r configs/bspwm/* ~/.config/bspwm/
    cp -r configs/sxhkd/* ~/.config/sxhkd/
    cp -r configs/polybar/* ~/.config/polybar/

    chmod +x ~/.config/bspwm/bspwmrc 2>/dev/null || true
    chmod +x ~/.config/polybar/*.sh 2>/dev/null || true
}

### --- RUN --- ###
install_pkgs
install_configs
setup_wifi_resume

log "ГОТОВО. Перезапусти систему."
