'''
Lights RGB LED. This module must be run using subprocess with RGB color value list as argument
'''
import board
import neopixel
import argparse
import json

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('colorVal', type = str)
args = parser.parse_args()
colorVal = args.colorVal
colorVal = json.loads(colorVal)
# Light the rgb led
pixels = neopixel.NeoPixel(board.D10, 1, brightness = 1, auto_write = False, bpp = 8)
pixels[0] = colorVal
pixels.show()

