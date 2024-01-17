import subprocess
from PIL import Image
import colorsys

MAX_SATURATION_VALUE    = 100
MIN_VALUE_VALUE         = 50

START_SATURATION_VALUE    = 50
START_VALUE_VALUE         = 100

def hsv_to_hex (hsv_colors):
    hex_colors = []
    for color in hsv_colors:
        rgb_color = colorsys.hsv_to_rgb(color[0]/360., color[1]/100., color[2]/100.)
        rgb_color = tuple(round(x * 255) for x in rgb_color)
        hex_color = '#%02x%02x%02x' % rgb_color
        hex_colors.append(hex_color)

    return hex_colors

def get_base_color (wallpaper_path):
    img = Image.open(wallpaper_path).convert('HSV')
    img = img.resize((1, 1), Image.Resampling.LANCZOS)
    base_color = img.getpixel((0, 0))
    base_color = int(base_color[0]*(360/255)), int(base_color[1]*(100/255)), int(base_color[2]*(100/255))
    return base_color

def generate_colors(base_color, num_colors):
    start_color = (base_color[0], START_SATURATION_VALUE, START_VALUE_VALUE)
    hsv_colors = []
    saturation_step = int((MAX_SATURATION_VALUE - START_SATURATION_VALUE) / num_colors)
    value_step = int((START_VALUE_VALUE - MIN_VALUE_VALUE) / num_colors)
    for i in range(num_colors):
        color = (start_color[0], start_color[1] + i * saturation_step, start_color[2] - i * value_step)
        hsv_colors.append(color)

    return hsv_to_hex(hsv_colors)

def get_wallpaper ():
    theme = subprocess.run(
        'gsettings get org.gnome.desktop.interface color-scheme',
        capture_output=True,
        shell=True,
        universal_newlines=True
    ).stdout.strip().replace("'", '')

    theme_key = 'picture-uri-dark' if theme == 'prefer-dark' else 'picture-uri'
    wallpaper_path = subprocess.run(
        f'gsettings get org.gnome.desktop.background {theme_key}',
        capture_output=True,
        shell=True,
        universal_newlines=True
    ).stdout.strip().replace("'", '').replace('file://', '')

    return wallpaper_path

def modify_svg(input_file, output_file, base_color):
    with open(input_file, 'r') as file:
        svg_content = file.read()
    elements = svg_content.split('\n')

    fill_number = 0
    for element in elements:
        if 'fill' in element: fill_number += 1
    
    color_index = 0
    colors = generate_colors(base_color, fill_number)
    for i in range(0, len(elements)):
        element = elements[i]

        separator = ''
        if 'fill:' in element:
            separator = 'fill:'
        else:
            separator = 'fill="'

        # REFACTOR
        start_index = element.find(separator) + len(separator)
        end_index = element.find('"', start_index)
        original_color = element[start_index:end_index]
        
        new_color = colors[color_index % len(colors)]
        modified_element = element.replace(f'{separator}{original_color}"', f'{separator}{new_color}"')
        
        elements[i] = modified_element
        
        color_index += 1
    
    modified_svg_content = '\n'.join(elements)
    
    with open(output_file, 'w') as file:
        file.write(modified_svg_content)

if __name__ == '__main__':
    input_svg_file = 'icon2.svg'
    output_svg_file = 'output_icon.svg'
    
    base_color = get_base_color(get_wallpaper())
    modify_svg(input_svg_file, output_svg_file, base_color)
    
