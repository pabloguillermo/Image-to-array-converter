# Image-to-array-converter v1.0.1

## Changes in 1.0.1

- New window: choose a folder, compatible images (JPG, JPEG, PNG, BMP, GIF) are listed automatically with a preview on the right
- Built-in folder picker that opens large and fits small screens
- Valid C identifiers for file names with spaces, hyphens or leading digits

## Overview

This release adds a Python-based image converter that converts JPG/PNG files into RGB565 arrays suitable for TFT displays and Arduino/ESP32 projects.

## Included

- Python app to select and convert images
- Generation of `.h` files with RGB565 arrays
- Debian package build workflow
- Windows executable build workflow via PyInstaller

## Usage

1. Run the app and select a JPG or PNG image.
2. The script generates a `.h` file next to the source image.
3. Include the generated header in your Arduino/TFT_eSPI project.

## Notes

- For sprites, the image resolution should be equal to or smaller than the display resolution.
- If an image is larger than the display, it should be resized before conversion.

## Files

- Debian package: `conversor-image-array_1.0.1_all.deb`
- Windows binary: `ImageToArrayConverter.exe`
