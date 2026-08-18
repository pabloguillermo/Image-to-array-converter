#!/usr/bin/env python3
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image


def convert_image_to_header(image_path):
    try:
        file_dir = os.path.dirname(image_path)
        file_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}.h")

        img = Image.open(image_path)
        img = img.convert("RGB")

        width, height = img.size
        rgb565_array = []

        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))

                r5 = (r >> 3) & 0x1F
                g6 = (g >> 2) & 0x3F
                b5 = (b >> 3) & 0x1F

                rgb565 = (r5 << 11) | (g6 << 5) | b5
                rgb565_array.append(rgb565)

        header_content = f"#ifndef {file_name.upper()}_H\n#define {file_name.upper()}_H\n\n"
        header_content += "#include <stdint.h>\n\n"
        header_content += f"const uint16_t {file_name}[] = {{\n"

        for i, pixel in enumerate(rgb565_array):
            header_content += f" 0x{pixel:04x},"
            if (i + 1) % 16 == 0:
                header_content += "\n"

        header_content = header_content.rstrip(",\n")
        header_content += f"\n}};\n\n#endif // {file_name.upper()}_H\n"

        with open(output_path, "w") as header_file:
            header_file.write(header_content)

        print(f"Arquivo de header gerado com sucesso: {output_path}")

    except Exception as e:
        print(f"Erro: {e}")


def select_image_and_convert():
    print("Por favor, selecione o arquivo de imagem...")
    Tk().withdraw()
    image_path = askopenfilename(filetypes=[("Imagens", "*.jpg;*.png")])
    if image_path:
        convert_image_to_header(image_path)
    else:
        print("Nenhum arquivo selecionado.")


if __name__ == "__main__":
    select_image_and_convert()
