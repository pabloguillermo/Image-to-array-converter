#!/usr/bin/env python3
import base64
import io
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image

# Extensões de imagem compatíveis
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
PREVIEW_SIZE = (320, 320)


def list_compatible_files(folder):
    """Retorna os nomes dos arquivos de imagem compatíveis na pasta."""
    try:
        names = os.listdir(folder)
    except OSError:
        return []
    return sorted(
        (n for n in names
         if n.lower().endswith(SUPPORTED_EXTENSIONS) and os.path.isfile(os.path.join(folder, n))),
        key=str.lower,
    )


def convert_image_to_header(image_path):
    """Converte a imagem para um header C com array RGB565. Retorna o caminho de saída."""
    # Obter o nome e a pasta do arquivo de origem
    file_dir = os.path.dirname(image_path)
    file_name = os.path.splitext(os.path.basename(image_path))[0]  # Nome sem extensão
    # Nome válido como identificador C
    identifier = re.sub(r"\W", "_", file_name)
    if identifier[0].isdigit():
        identifier = "_" + identifier
    output_path = os.path.join(file_dir, f"{file_name}.h")  # Arquivo de saída com extensão .h

    with Image.open(image_path) as img:
        img = img.convert("RGB")  # Garantir que está no formato RGB
        pixels = list(img.getdata())

    # Converter para RGB565
    rgb565_array = [((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3) for r, g, b in pixels]

    guard = f"{identifier.upper()}_H"
    lines = []
    for i in range(0, len(rgb565_array), 16):  # 16 valores por linha
        lines.append(" " + ", ".join(f"0x{p:04x}" for p in rgb565_array[i:i + 16]))

    header_content = (
        f"#ifndef {guard}\n#define {guard}\n\n"
        f"#include <stdint.h>\n\n"
        f"const uint16_t {identifier}[] = {{\n"
        + ",\n".join(lines)
        + f"\n}};\n\n#endif // {guard}\n"
    )

    with open(output_path, "w") as header_file:
        header_file.write(header_content)

    return output_path


class FolderDialog(tk.Toplevel):
    """Seletor de pastas próprio, já aberto em tamanho grande (limitado à tela)."""

    def __init__(self, parent, initialdir):
        super().__init__(parent)
        self.title("Selecione a pasta com as imagens")
        self.result = None
        self.path = initialdir if os.path.isdir(initialdir) else os.path.expanduser("~")

        width = min(900, int(self.winfo_screenwidth() * 0.9))
        height = min(700, int(self.winfo_screenheight() * 0.9))
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(min(400, width), min(300, height))

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="↑ Subir", command=self.go_up).pack(side="left")
        ttk.Button(top, text="Início", command=lambda: self.navigate(os.path.expanduser("~"))).pack(
            side="left", padx=(4, 0))
        self.entry = ttk.Entry(top)
        self.entry.pack(side="left", fill="x", expand=True, padx=8)
        self.entry.bind("<Return>", lambda e: self.navigate(self.entry.get()))

        # Botões primeiro no pack, para nunca ficarem fora da janela
        bottom = ttk.Frame(self, padding=8)
        bottom.pack(side="bottom", fill="x")
        ttk.Button(bottom, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(bottom, text="Selecionar esta pasta", command=self.accept).pack(side="right", padx=4)

        mid = ttk.Frame(self, padding=(8, 0))
        mid.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(mid, orient="vertical")
        self.listbox = tk.Listbox(mid, activestyle="none", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", self.open_selected)
        self.listbox.bind("<Return>", self.open_selected)

        self.navigate(self.path)
        self.transient(parent)
        self.grab_set()
        self.listbox.focus_set()
        self.wait_window()

    def navigate(self, path):
        path = os.path.abspath(os.path.expanduser(path))
        try:
            dirs = sorted((n for n in os.listdir(path)
                           if not n.startswith(".") and os.path.isdir(os.path.join(path, n))),
                          key=str.lower)
        except OSError as e:
            messagebox.showerror("Erro", str(e), parent=self)
            self.entry.delete(0, "end")
            self.entry.insert(0, self.path)
            return
        self.path = path
        self.entry.delete(0, "end")
        self.entry.insert(0, path)
        self.listbox.delete(0, "end")
        for name in dirs:
            self.listbox.insert("end", name)

    def go_up(self):
        self.navigate(os.path.dirname(self.path))

    def open_selected(self, _event=None):
        sel = self.listbox.curselection()
        if sel:
            self.navigate(os.path.join(self.path, self.listbox.get(sel[0])))

    def accept(self):
        self.result = self.path
        self.destroy()


class App:
    def __init__(self, root):
        self.root = root
        self.folder = None
        self.photo = None  # Referência para evitar coleta de lixo da imagem
        root.title("Image to Array Converter")
        root.geometry("760x460")
        root.minsize(620, 360)

        # Barra superior: seleção da pasta
        top = ttk.Frame(root, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Selecionar pasta...", command=self.choose_folder).pack(side="left")
        self.folder_label = ttk.Label(top, text="Nenhuma pasta selecionada", anchor="w")
        self.folder_label.pack(side="left", fill="x", expand=True, padx=8)

        # Área central: lista à esquerda, visualizador à direita
        body = ttk.Frame(root, padding=(8, 0))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(body, text="Imagens compatíveis", padding=4)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.listbox = tk.Listbox(list_frame, activestyle="none", exportselection=False,
                                  yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self.convert_selected())

        preview_frame = ttk.LabelFrame(body, text="Visualização", padding=4)
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self.preview = ttk.Label(preview_frame, anchor="center")
        self.preview.pack(fill="both", expand=True)
        self.info = ttk.Label(preview_frame, anchor="center")
        self.info.pack(fill="x")

        # Barra inferior: ação e status
        bottom = ttk.Frame(root, padding=8)
        bottom.pack(fill="x")
        self.status = ttk.Label(bottom, text="Selecione uma pasta para começar.", anchor="w")
        self.status.pack(side="left", fill="x", expand=True)
        self.convert_btn = ttk.Button(bottom, text="Converter para .h",
                                      command=self.convert_selected, state="disabled")
        self.convert_btn.pack(side="right")

    def choose_folder(self):
        folder = FolderDialog(self.root, self.folder or os.path.expanduser("~")).result
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder):
        self.folder = folder
        self.folder_label.config(text=folder)
        files = list_compatible_files(folder)
        self.listbox.delete(0, "end")
        for name in files:
            self.listbox.insert("end", name)
        self.clear_preview()
        self.convert_btn.config(state="disabled")
        if files:
            self.status.config(text=f"{len(files)} imagem(ns) compatível(is) encontrada(s).")
            self.listbox.selection_set(0)
            self.on_select()
        else:
            self.status.config(text="Nenhuma imagem compatível encontrada nesta pasta.")

    def selected_path(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return os.path.join(self.folder, self.listbox.get(sel[0]))

    def clear_preview(self):
        self.photo = None
        self.preview.config(image="", text="")
        self.info.config(text="")

    def on_select(self, _event=None):
        path = self.selected_path()
        if not path:
            return
        self.convert_btn.config(state="normal")
        try:
            with Image.open(path) as img:
                size = img.size
                thumb = img.convert("RGB")
            thumb.thumbnail(PREVIEW_SIZE)
            buf = io.BytesIO()
            thumb.save(buf, format="PNG")
            # PhotoImage do Tk lê PNG direto, sem precisar de PIL.ImageTk
            self.photo = tk.PhotoImage(data=base64.b64encode(buf.getvalue()))
            self.preview.config(image=self.photo, text="")
            self.info.config(text=f"{size[0]} x {size[1]} px")
        except Exception as e:
            self.clear_preview()
            self.preview.config(text=f"Não foi possível abrir a imagem:\n{e}")

    def convert_selected(self):
        path = self.selected_path()
        if not path:
            return
        try:
            output = convert_image_to_header(path)
            self.status.config(text=f"Gerado: {output}")
        except Exception as e:
            self.status.config(text="Erro na conversão.")
            messagebox.showerror("Erro", str(e))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
