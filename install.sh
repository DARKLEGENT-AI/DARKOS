#!/usr/bin/env bash
set -e

log() {
    echo -e "\e[41;97m=== $1 ===\e[0m"
}

### --- Пакеты --- ###
install_pkgs() {
    log "Установка основных пакетов Debain (Необходимо устанавливать под пользователем, не под root !)"
    sudo apt update
    sudo apt install -y \
        bspwm sxhkd polybar rofi feh picom \
        pulseaudio pavucontrol \
        bluez blueman xinput xbacklight pipewire pipewire-audio wireplumber libspa-0.2-bluetooth \
        git gh curl unzip \
        firmware-misc-nonfree network-manager \
        nemo alacritty pamixer brightnessctl neofetch
    log "Установка доп пакетов"
    sudo apt install -y \
        firefox-esr thunderbird  \
        chromium xinit flameshot
    log "Установка темы rofi"
    sudo cp ~/DARKOS/configs/DARKOS.RASI /usr/share/rofi/themes/

    ### --- Установка SDDM ---
    log "Установка SDDM"
    sudo apt install -y sddm
    log "Включение SDDM как дисплей менеджера"
    sudo systemctl enable sddm.service
    sudo systemctl set-default graphical.target
}

### --- Копирование конфигов --- ###
install_configs() {
    log "Копирование конфигов"

    mkdir -p ~/.config/bspwm ~/.config/sxhkd ~/.config/polybar

    cp -r configs/bspwm/* ~/.config/bspwm/
    cp -r configs/sxhkd/* ~/.config/sxhkd/
    cp -r configs/polybar/* ~/.config/polybar/
    cp -r configs/flameshot/* ~/.config/flameshot/

    chmod +x ~/.config/bspwm/bspwmrc 2>/dev/null || true
    chmod +x ~/.config/polybar/*.sh 2>/dev/null || true
}

### --- RUN --- ###
install_pkgs
install_configs

### --- Создание .xinitrc для запуска startx --- ###
log "Создание ~/.xinitrc для запуска окружения через startx"
cat <<'EOF' > ~/.xinitrc
#!/bin/sh
# Восстановление фона и запуск сервисов
nitrogen --restore &
picom &
sxhkd &
# Запуск bspwm
exec bspwm
EOF
chmod +x ~/.xinitrc


log "ГОТОВО. Перезапусти систему."
