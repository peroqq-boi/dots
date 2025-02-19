import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class WallpaperApp:
    def __init__(self):
        # Initialize variables
        self.wallpapers_dir = os.path.expanduser('~/.config/Wallpapers')
        self.wallpaper_files = self.get_image_files(self.wallpapers_dir)
        self.wallpaper_thumbnails = []
        self.selected_index = 0

        # Load colors from colors.styl
        self.load_colors_from_file()  # Load colors into self.colors

        # Create Tkinter window
        self.window = tk.Tk()
        self.window.title("Wallpaper Selector")
        self.window.geometry('500x500')
        self.window.config(bg=self.colors.get('background', '#1e1e1e'))  # Use the loaded background color or default

        # Title label
        title_label = tk.Label(self.window, text="Wallpaper Selector", font=("Helvetica", 20, "bold"),
                               fg=self.colors.get('color15', '#ffffff'), bg=self.colors.get('background', '#1e1e1e'))
        title_label.pack(pady=20)

        # Canvas for thumbnails
        self.canvas = tk.Canvas(self.window, bg=self.colors.get('background', '#1e1e1e'))
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar for canvas
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=scrollbar.set)

        # Frame to hold thumbnail buttons
        self.thumbnail_frame = tk.Frame(self.canvas, bg=self.colors.get('background', '#1e1e1e'))
        self.canvas.create_window((0, 0), window=self.thumbnail_frame, anchor="nw")

        # Load wallpapers and update thumbnail buttons
        self.reload_wallpapers()

        # Add control buttons (at the bottom)
        self.button_frame = tk.Frame(self.window, bg=self.colors.get('background', '#1e1e1e'))
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Create the buttons horizontally, using color6 for button background
        button_width = 20
        self.create_button("Set Wallpaper for DP-3", self.select_wallpaper_for_dp3, self.colors.get('color6', '#455648'), button_width)
        self.create_button("Set Wallpaper for HDMI-A-1", self.select_wallpaper_for_hdmi1, self.colors.get('color6', '#455648'), button_width)
        self.create_button("Set Wallpaper for Both Monitors", lambda: self.set_wallpaper_for_both_monitors(self.wallpaper_files[self.selected_index]), self.colors.get('color6', '#455648'), button_width)
        self.create_button("Change SDDM Wallpaper", self.change_sddm_wallpaper, self.colors.get('color6', '#455648'), button_width)
        self.create_button("Change Wallpaper Directory", self.change_wallpapers_directory, self.colors.get('color6', '#455648'), button_width)

        # Bind keys for navigation and actions
        self.window.bind('w', self.navigate_thumbnails)  # Up
        self.window.bind('s', self.navigate_thumbnails)  # Down
        self.window.bind('a', self.navigate_thumbnails)  # Left
        self.window.bind('d', self.navigate_thumbnails)  # Right
        self.window.bind('1', self.select_wallpaper_for_dp3)
        self.window.bind('2', self.select_wallpaper_for_hdmi1)
        self.window.bind('3', lambda event: self.set_wallpaper_for_both_monitors(self.wallpaper_files[self.selected_index]))
        self.window.bind('4', self.change_sddm_wallpaper)

    def get_image_files(self, directory):
        supported_extensions = ['.jpg', '.png', '.gif']
        return [f for f in os.listdir(directory) if any(f.endswith(ext) for ext in supported_extensions)]

    def reload_wallpapers(self):
        # Check if the directory exists
        if not os.path.isdir(self.wallpapers_dir):
            print(f"Error: Directory does not exist: {self.wallpapers_dir}")
            return

        self.wallpaper_files = self.get_image_files(self.wallpapers_dir)
        if not self.wallpaper_files:
            print("No wallpaper files found in the directory.")
            return

        self.wallpaper_thumbnails = []

        # Reload the thumbnails
        for wallpaper in self.wallpaper_files:
            wallpaper_path = os.path.join(self.wallpapers_dir, wallpaper)
            if not os.path.exists(wallpaper_path):
                print(f"Error: File not found: {wallpaper_path}")
                continue

            image = Image.open(wallpaper_path)
            image.thumbnail((100, 100))  # Thumbnail size set to 100x100 px
            img = ImageTk.PhotoImage(image)
            self.wallpaper_thumbnails.append((img, wallpaper))  # Include the filename

        self.update_thumbnail_buttons()

    def update_thumbnail_buttons(self):
        # Update buttons with thumbnails and highlight the selected one
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()

        for index, (thumbnail, filename) in enumerate(self.wallpaper_thumbnails):
            border_color = "pink" if index == self.selected_index else "#333"
            thumbnail_button = tk.Button(self.thumbnail_frame, image=thumbnail, command=lambda i=index: self.update_selected_index(i),
                                         relief="solid", bd=2, highlightbackground=border_color, highlightthickness=3,
                                         width=100, height=100)  # Ensure button size is fixed

            # Truncate filenames to 12 characters (to ensure neat appearance)
            short_filename = filename[:12] + ('...' if len(filename) > 12 else '')

            # Add label with the truncated filename below the thumbnail
            label = tk.Label(self.thumbnail_frame, text=short_filename, font=("Arial", 10), fg=self.colors.get('color15', '#ffffff'), bg=self.colors.get('background', '#1e1e1e'))
            thumbnail_button.grid(row=index // 9, column=index % 9, padx=10, pady=10)


        # Update scroll region
        self.thumbnail_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))  # Adjust the scroll region

    def update_selected_index(self, index):
        self.selected_index = index
        self.update_thumbnail_buttons()

    def navigate_thumbnails(self, event):
        if event.keysym == 'w':  # Up
            self.selected_index = (self.selected_index - 5) % len(self.wallpaper_files)
        elif event.keysym == 's':  # Down
            self.selected_index = (self.selected_index + 5) % len(self.wallpaper_files)
        elif event.keysym == 'a':  # Left
            self.selected_index = (self.selected_index - 1) % len(self.wallpaper_files)
        elif event.keysym == 'd':  # Right
            self.selected_index = (self.selected_index + 1) % len(self.wallpaper_files)

        # Use after to ensure smooth image change and avoid flickering
        self.window.after(50, self.update_thumbnail_buttons)

    def select_wallpaper_for_dp3(self, event=None):
        wallpaper_path = os.path.join(self.wallpapers_dir, self.wallpaper_files[self.selected_index])
        self.set_wallpaper(wallpaper_path, "DP-3")
        self.apply_wall_colors(wallpaper_path)

    def select_wallpaper_for_hdmi1(self, event=None):
        wallpaper_path = os.path.join(self.wallpapers_dir, self.wallpaper_files[self.selected_index])
        self.set_wallpaper(wallpaper_path, "HDMI-A-1")
        # No need to apply wall colors for HDMI-A-1

    def set_wallpaper(self, wallpaper_path, monitor):
        # Before setting the wallpaper, check if the file exists
        if not os.path.exists(wallpaper_path):
            print(f"Error: File not found: {wallpaper_path}")
            return

        print(f"Setting wallpaper for {monitor}: {wallpaper_path}")  # Log to console
        subprocess.run(['swww', 'img', wallpaper_path, '--outputs', monitor])

    def set_wallpaper_for_both_monitors(self, wallpaper_path):
        # Before setting the wallpaper, check if the file exists
        if not os.path.exists(wallpaper_path):
            print(f"Error: File not found: {wallpaper_path}")
            return

        print(f"Setting wallpaper for both monitors: {wallpaper_path}")  # Log to console
        subprocess.run(['swww', 'img', wallpaper_path])  # Without '--outputs'

    def change_sddm_wallpaper(self):
        answer = messagebox.askyesno("Change SDDM Wallpaper", "Do you want to change the SDDM wallpaper?")
        if answer:
            wallpaper_path = os.path.join(self.wallpapers_dir, self.wallpaper_files[self.selected_index])

            # Check if file exists before proceeding
            if not os.path.exists(wallpaper_path):
                print(f"Error: File not found: {wallpaper_path}")
                return

            subprocess.run(['kitty', '-e', 'sudo', 'cp', wallpaper_path, '/usr/share/sddm/themes/simplicity/images/background.jpg'])

    def change_wallpapers_directory(self):
        new_dir = filedialog.askdirectory(title="Select Wallpapers Folder", initialdir=self.wallpapers_dir)
        if new_dir and os.path.isdir(new_dir):
            self.wallpapers_dir = new_dir
            self.reload_wallpapers()

    def create_button(self, text, command, color, width):
        button = tk.Button(self.button_frame, text=text, command=command, font=("Arial", 12), fg=self.colors.get('color15', '#ffffff'), bg=color, activebackground="#444", relief="flat", bd=2, width=width)
        button.pack(side=tk.LEFT, padx=10)  # Use side=tk.LEFT to arrange buttons horizontally
        return button

    def load_colors_from_file(self):
        # Read the .styl file content
        colors_styl_path = os.path.expanduser('~/.cache/wal/colors.styl')
        try:
            with open(colors_styl_path, 'r') as file:
                colors_styl_content = file.read()
                self.colors = self.parse_colors(colors_styl_content)
                print(f"Loaded colors: {self.colors}")
        except FileNotFoundError:
            print(f"Error: The file {colors_styl_path} was not found.")
            self.colors = {}  # Fallback in case the file doesn't exist

    def parse_colors(self, colors_styl_content):
        # Initializing a dictionary to hold the colors
        colors = {}

        # Loop through each line in the colors.styl content
        for line in colors_styl_content.splitlines():
            line = line.strip()  # Clean up extra spaces
            # Check for the colors we are interested in and add them to the dictionary
            if line.startswith('$background:'):
                colors['background'] = line.split(':')[1].strip().strip(';')
            elif line.startswith('$color15:'):
                colors['color15'] = line.split(':')[1].strip().strip(';')
            elif line.startswith('$color6:'):
                colors['color6'] = line.split(':')[1].strip().strip(';')

        return colors

    def apply_wall_colors(self, wallpaper_path):
        # This will only run when changing the wallpaper on DP-3
        print(f"Applying wall colors for: {wallpaper_path}")  # Log to console
        # Generate colors from wal, but without changing the wallpaper
        subprocess.run(['wal', '-n', '-e', '--cols16', '-q', '-i', wallpaper_path])

        # Copy the color file to the Hyprland configuration
        subprocess.run(['cp', os.path.expanduser('~/.cache/wal/colors-hyprland'), os.path.expanduser('~/.config/hypr/colors.conf')])

        # Apply pywal colors to GTK applications
        subprocess.run(['gradience-cli', 'apply', '-n', 'pywal', '--gtk', 'both'])

        # Update pywalfox
        subprocess.run(['pywalfox', 'update'])

        # Run pywal Python script
        subprocess.run(['python', os.path.expanduser('/home/user721/Scripts/pywal.py')])

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = WallpaperApp()
    app.run()
