import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image

def convert_image_to_header(image_path):
    try:
        # Obter o nome e a pasta do arquivo de origem
        file_dir = os.path.dirname(image_path)
        file_name = os.path.splitext(os.path.basename(image_path))[0]  # Nome sem extensão
        output_path = os.path.join(file_dir, f"{file_name}.h")  # Arquivo de saída com extensão .h

        # Abrir a imagem usando PIL
        img = Image.open(image_path)
        img = img.convert("RGB")  # Garantir que está no formato RGB

        # Obter dimensões da imagem
        width, height = img.size

        # Criar lista para armazenar os pixels em formato RGB565
        rgb565_array = []

        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))

                # Converter para RGB565
                r5 = (r >> 3) & 0x1F
                g6 = (g >> 2) & 0x3F
                b5 = (b >> 3) & 0x1F

                rgb565 = (r5 << 11) | (g6 << 5) | b5
                rgb565_array.append(rgb565)

        # Criar o conteúdo do arquivo de header
        header_content = f"#ifndef {file_name.upper()}_H\n#define {file_name.upper()}_H\n\n"
        header_content += f"#include <stdint.h>\n\n"
        header_content += f"const uint16_t {file_name}[] = {{\n"

        # Adicionar os valores do array no header, com 16 por linha
        for i, pixel in enumerate(rgb565_array):
            header_content += f" 0x{pixel:04x},"
            if (i + 1) % 16 == 0:  # Quebrar linha a cada 16 valores
                header_content += "\n"

        header_content = header_content.rstrip(",\n")  # Remover última vírgula e nova linha
        header_content += f"\n}};\n\n#endif // {file_name.upper()}_H\n"

        # Escrever o arquivo de header
        with open(output_path, "w") as header_file:
            header_file.write(header_content)

        print(f"Arquivo de header gerado com sucesso: {output_path}")

    except Exception as e:
        print(f"Erro: {e}")

# Configurar a janela de seleção de arquivo
def select_image_and_convert():
    print("Por favor, selecione o arquivo de imagem...")
    Tk().withdraw()  # Ocultar janela principal
    image_path = askopenfilename(filetypes=[("Imagens", "*.jpg;*.png")])  # Abrir janela de seleção
    if image_path:
        convert_image_to_header(image_path)
    else:
        print("Nenhum arquivo selecionado.")

# Executar o programa
if __name__ == "__main__":
    select_image_and_convert()