import re
import os

# File paths
colors_css_path = os.path.expanduser('~/.cache/wal/colors.css')
browser_css_path = os.path.expanduser('~/.config/browser/style.css')

# Function to get colors from the colors.css file
def get_colors_from_colors_css():
    colors = {}
    with open(colors_css_path, 'r') as f:
        content = f.read()
        # Regex to find colors in the format --colorX: #hex
        color_matches = re.findall(r'--(\w+):\s*#(\w+);', content)
        for color_name, hex_value in color_matches:
            colors[color_name] = hex_value
    return colors

# Function to update colors in style.css
def update_browser_style_css(colors):
    with open(browser_css_path, 'r') as f:
        content = f.read()

    # Replace colors in style.css
    for color_name, hex_value in colors.items():
        # Replace each color variable in the format --colorX in style.css
        content = re.sub(r'(--' + color_name + r':\s*#\w+)', f'--{color_name}: #{hex_value}', content)

    # Save the updated file
    with open(browser_css_path, 'w') as f:
        f.write(content)

# Get the colors
colors = get_colors_from_colors_css()

# Update style.css
update_browser_style_css(colors)

print("The colors have been updated in ~/.config/browser/style.css.")
