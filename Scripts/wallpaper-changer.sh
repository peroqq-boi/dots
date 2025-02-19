#!/bin/bash

# Check if dialog is installed
if ! command -v dialog &> /dev/null; then
    echo "Dialog is not installed. Installing dialog..."
    sudo pacman -S dialog
fi

# Path to the wallpapers folder (changed to Wallpapers)
wallpapers_dir="$HOME/Pictures/Wallpapers/"

# Check if the wallpapers folder exists
if [ ! -d "$wallpapers_dir" ]; then
    dialog --title "Error" --msgbox "The wallpapers folder '$wallpapers_dir' does not exist." 8 50
    exit 1
fi

# Change to the wallpapers folder
cd "$wallpapers_dir" || { dialog --title "Error" --msgbox "Failed to navigate to folder '$wallpapers_dir'" 8 50; exit 1; }

# Display available files in the folder (only images)
available_wallpapers=$(find . -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.gif" \))

# Create a list of files to choose from
wallpapers_list=()
for wallpaper in $available_wallpapers; do
    wallpapers_list+=("$(basename "$wallpaper")" "")
done

# Choose a wallpaper for monitor DP-3
wall_dp3=$(dialog --title "Choose Wallpaper for DP-3" --menu "Select a wallpaper for DP-3:" 15 50 6 "${wallpapers_list[@]}" 3>&1 1>&2 2>&3)

# If the user canceled the selection
if [ -z "$wall_dp3" ]; then
    exit 1
fi

# Set the wallpaper using swww
swww img "$wallpapers_dir/$wall_dp3" --outputs DP-3

# Generate colors from wal, but without changing the wallpaper
wal -n -e --cols16 -q -i "$wallpapers_dir/$wall_dp3"

# Copy the color file to the Hyprland configuration
cp ~/.cache/wal/colors-hyprland ~/.config/hypr/colors.conf

rm -rf /home/user721/.config/youwal/youwal.css

/home/user721/Pictures/Youwal/youwal

gradience-cli apply -n pywal --gtk both

pywalfox update

python /home/user721/Scripts/pywal.py

# Choose a wallpaper for monitor HDMI-A-1
wall_hdmi1=$(dialog --title "Choose Wallpaper for HDMI-A-1" --menu "Select a wallpaper for HDMI-A-1:" 15 50 6 "${wallpapers_list[@]}" 3>&1 1>&2 2>&3)

# If the user canceled the selection
if [ -z "$wall_hdmi1" ]; then
    exit 1
fi

# Check if swww-daemon is running
if ! pgrep -x "swww-daemon" > /dev/null; then
    swww-daemon &
fi

# Set wallpapers on the respective monitors
swww img "$wallpapers_dir/$wall_hdmi1" --outputs HDMI-A-1

# Ask if we want to change the wallpaper for SDDM
dialog --title "Do you want to change the SDDM wallpaper?" --yesno "Do you want to change the wallpaper for SDDM?" 7 50

# Check what response was selected
if [ $? -eq 0 ]; then  # If the response is "Yes" (0 is "Yes")
    # Choose a wallpaper for SDDM
    wall_sddm=$(dialog --title "Choose Wallpaper for SDDM" --menu "Select a wallpaper for SDDM:" 15 50 6 "${wallpapers_list[@]}" 3>&1 1>&2 2>&3)

    # If the user canceled the selection
    if [ -z "$wall_sddm" ]; then
        exit 1
    fi

    # Copy the selected wallpaper to the SDDM background folder
    sudo cp "$wallpapers_dir/$wall_sddm" /usr/share/sddm/themes/simplicity/images/background.jpg

    # Set appropriate permissions for the file (if necessary)
    sudo chmod 644 /usr/share/sddm/themes/simplicity/images/background.jpg
fi

# End of the script
exit 0
