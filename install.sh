#!/bin/bash

# Function to install Snapper and perform basic configuration
install_snapper() {
    read -p "Do you want to install Snapper and perform basic configuration? (y/n): " install_snapper
    if [[ "$install_snapper" == "y" || "$install_snapper" == "Y" ]]; then
        echo "Installing snapper-support..."
        yay -S --noconfirm snapper-support

        echo "Creating Snapper configuration for /home..."
        sudo snapper -c home create-config /home

        echo "Creating Snapper configuration for /..."
        sudo snapper -c root create-config /

        echo "Modifying timeline settings for /home and / to not create snapshots..."
        sudo sed -i 's/^TIMELINE_CREATE="yes"/TIMELINE_CREATE="no"/' /etc/snapper/configs/home
        sudo sed -i 's/^TIMELINE_CREATE="yes"/TIMELINE_CREATE="no"/' /etc/snapper/configs/root

        echo "Creating snapshots for /home and / with description 'FRESH'..."
        sudo snapper -c home create -d "FRESH"
        sudo snapper -c root create -d "FRESH"
    else
        echo "Not installing Snapper."
    fi
}

# Function to install pacman and yay packages
install_packages() {
    pacman_packages=(
        hyprland kitty sddm thunar gvfs waybar wofi fastfetch kate hyprlock hypridle kvantum
        nwg-look adw-gtk-theme qt5ct qt6ct hyprcursor ark hyprpicker wl-clipboard vlc
        xdg-desktop-portal-hyprland grim slurp kvantum-qt5 gwenview kcalc
        xwaylandvideobridge ttf-meslo-nerd btop qt6-5compat qt6-declarative
        qt5-graphicaleffects qt5-wayland qt6-wayland print-manager obs-studio tumbler ffmpegthumbnailer
        libreoffice jdk11-openjdk swww swaync
    )

    yay_packages=(
        btrfs-assistant hyprpolkitagent python-pywal16 youtube-music-bin
        gradience rose-pine-hyprcursor update-grub python-pywalfox-librewolf
        vscodium-bin clipse simplicity-sddm-theme rose-pine-cursor
        epson-inkjet-printer-escpr epsonscan2 paccache-hook planify
        freetube librewolf-bin wlogout libresprite-bin pixelorama-bin tint
    )

    echo "Installing packages from pacman..."
    sudo pacman -S --noconfirm --needed "${pacman_packages[@]}"

    echo "Installing packages from yay..."
    yay -S --noconfirm --needed "${yay_packages[@]}"
}

# Function to create directories
create_folders() {
    if [ ! -d "$HOME/Documents" ]; then
        echo "Documents folder does not exist. Creating it..."
        mkdir "$HOME/Documents"
    fi
    mkdir -p "$HOME/Documents/Prints"
    mkdir -p "$HOME/Documents/Scans"
    mkdir -p "$HOME/Documents/Prints/Templates"
    mkdir -p "$HOME/Documents/Prints/Mama"
    mkdir -p "$HOME/Documents/Prints/School"

    if [ ! -d "$HOME/Videos" ]; then
        echo "Videos folder does not exist. Creating it..."
        mkdir "$HOME/Videos"
    fi
    mkdir -p "$HOME/Videos/Recordings"

    if [ ! -d "$HOME/Pictures" ]; then
        echo "Pictures folder does not exist. Creating it..."
        mkdir "$HOME/Pictures"
    fi
    mkdir -p "$HOME/Pictures/Screenshots"

    pywalfox install --browser librewolf

    echo "Folders have been created successfully!"
}

# Function to copy configuration files
copy_config_files() {
    echo "Copying .config folder to ~/.config..."
    cp -r config/* ~/.config
    cp -r Scripts ~/
    cp -r .bashrc ~/
    cp -r colors-hyprland ~/.config/wal/templates
}

# Function to install and configure Promixa
install_promixa() {
    current_dir=$(pwd)
    cd Promix/
    chmod +x promix.sh
    ./promix.sh install
    cd "$current_dir"
}

# Function to configure pywal and themes
configure_pywal() {
    mkdir -p ~/.config/wal/templates/
    cp pywal16-libadwaita/templates/* ~/.config/wal/templates/
    wal -i ~/Pictures/Wallpapers/a.jpg
    mkdir -p ~/.config/presets/user
    ln -s ~/.cache/wal/pywal.json ~/.config/presets/user/pywal.json
    mkdir -p ~/.config/Kvantum/pywal
    ln -s ~/.cache/wal/pywal.kvconfig ~/.config/Kvantum/pywal/pywal.kvconfig
    ln -s ~/.cache/wal/pywal.svg ~/.config/Kvantum/pywal/pywal.svg
}

# Function to update GRUB theme
update_grub_theme() {
    SOURCE_FOLDER="./aorus"
    TARGET_FOLDER="/usr/share/grub/themes/aorus"
    GRUB_FILE="/etc/default/grub"

    if [ ! -d "$SOURCE_FOLDER" ]; then
        echo "Folder 'aorus' does not exist in the current location."
        exit 1
    fi

    sudo cp -r "$SOURCE_FOLDER" "$TARGET_FOLDER"
    if [ ! -f "$GRUB_FILE" ]; then
        echo "File $GRUB_FILE does not exist."
        exit 1
    fi

    sudo sed -i 's/GRUB_GFXMODE=.*/GRUB_GFXMODE=1920x1080/' "$GRUB_FILE"
    sudo sed -i 's|#GRUB_THEME=".*"|GRUB_THEME="/usr/share/grub/themes/aorus/theme.txt"|' "$GRUB_FILE"

    if ! grep -q '^GRUB_THEME="/usr/share/grub/themes/aorus/theme.txt"' "$GRUB_FILE"; then
        sudo sed -i '/^#GRUB_THEME=/a GRUB_THEME="/usr/share/grub/themes/aorus/theme.txt"' "$GRUB_FILE"
    fi

    sudo update-grub
    echo "GRUB theme updated."
}

# Function to update SDDM theme
update_sddm_theme() {
    echo "Enabling SDDM service..."
    sudo systemctl enable sddm

    SOURCE_DIR="simplicity"
    DEST_DIR="/usr/share/sddm/themes"

    if [ -d "$SOURCE_DIR" ]; then
        sudo cp -r "$SOURCE_DIR" "$DEST_DIR"
    else
        echo "Source folder $SOURCE_DIR does not exist. Please ensure the path is correct."
        exit 1
    fi

    CONFIG_FILE="/etc/sddm.conf"

    if [ ! -f "$CONFIG_FILE" ]; then
        sudo touch "$CONFIG_FILE"
        echo "[Theme]" | sudo tee -a "$CONFIG_FILE" > /dev/null
        echo "Current=simplicity" | sudo tee -a "$CONFIG_FILE" > /dev/null
    else
        if grep -q "^Current=" "$CONFIG_FILE"; then
            sudo sed -i 's/^Current=.*/Current=simplicity/' "$CONFIG_FILE"
        else
            echo "[Theme]" | sudo tee -a "$CONFIG_FILE" > /dev/null
            echo "Current=simplicity" | sudo tee -a "$CONFIG_FILE" > /dev/null
        fi
    fi

    echo "SDDM theme updated."
}

librewolf_operations() {
    # Usunięcie folderu ~/.librewolf i skopiowanie folderu librewolf
    if [ -d "$HOME/.librewolf" ]; then
        echo "Usuwanie folderu ~/.librewolf..."
        rm -rf "$HOME/.librewolf"
    fi

    echo "Kopiowanie folderu librewolf do ~/.librewolf..."
    cp -r ./librewolf "$HOME/.librewolf"
}

# Function to update wallpapers and configure hyprland
update_wallpapers() {
    COUNTER_FILE="${HOME}/.local/state/counter.txt"
    COUNTER=$(cat "${COUNTER_FILE}")
    WALLPAPER_DIR="${HOME}/Pictures/Wallpapers"

    WALLPAPERS=()
    for w in "${WALLPAPER_DIR}"/*; do
        WALLPAPERS+=("${w}")
    done

    LEN=${#WALLPAPERS[@]}
    ((COUNTER++))
    COUNTER=$((COUNTER % LEN))
    echo "${COUNTER}" > "${COUNTER_FILE}"

    sudo snapper -c root create -d "FRESH AFTER"
    sudo snapper -c home create -d "FRESH AFTER"
}

# Function to restart computer
restart_computer() {
    read -p "Script finished. Do you want to restart the computer now? (y/n): " reboot_now
    if [[ "$reboot_now" == "y" || "$reboot_now" == "Y" ]]; then
        sudo reboot
    else
        echo "Please restart your computer manually to apply all changes."
    fi
}

# Main execution
install_snapper
install_packages
install_photopea
create_folders
copy_config_files
install_promixa
configure_pywal
update_grub_theme
update_sddm_theme
librewolf_operations
update_wallpapers
restart_computer
