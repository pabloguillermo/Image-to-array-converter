# Image-to-array-converter

This is a Python script to convert JPG/PNG images into byte arrays for use with TFT_eSPI.

## Overview

This project lets you select an image and generate a C header file with the pixels converted to RGB565 format, suitable for TFT displays and Arduino/ESP32 projects.

## Features

- Select an image through a file dialog
- Convert pixels to RGB565
- Generate a `.h` file automatically
- Works with sprites and bitmap-style graphics
- Linux and Windows release support

## Requirements

- Python 3.10+
- Pillow (`PIL`)
- Tkinter

## Linux installation

### Using apt

```bash
sudo apt update
sudo apt install python3-tk python3-pil
```

### Using a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pillow
```

## Run

```bash
python image_to_array.py
```

A file dialog will open. Choose the image and the script will generate a `.h` file next to it.

## Example output

```c
#ifndef IMG_H
#define IMG_H

#include <stdint.h>

const uint16_t img[] = {
  0xF800, 0x07E0, 0x001F, 0x0000,
  0xFFFF, 0x07FF, 0xF81F, 0x0000,
  0x0000, 0x001F, 0x07E0, 0xF800,
  0xFFFF, 0x07FF, 0xF81F, 0x0000
};

#endif // IMG_H
```

## TFT_eSPI usage

```cpp
#include "img.h"

TFT_eSPI tft = TFT_eSPI();

void setup() {
  tft.begin();
  tft.setRotation(1);
  tft.pushImage(0, 0, 4, 4, img);
}

void loop() {
}
```

## Resolution note

For sprites, the image resolution should be equal to or smaller than the display resolution.
If the image is larger than the display area, it should be resized before conversion.

## Debian package

The project includes a Debian packaging workflow and builds a `.deb` artifact via GitHub Actions.

## Windows release

The project also includes a PyInstaller workflow to generate a Windows `.exe` binary via GitHub Actions.

## License

This project is available for free use.
