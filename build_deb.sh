#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_DIR="$ROOT_DIR/debian_pkg"
OUT_DIR="$ROOT_DIR/dist"

mkdir -p "$OUT_DIR"
chmod 755 "$PKG_DIR/usr/bin/image_to_array"
chmod 755 "$PKG_DIR/usr/share/conversor-image-array/image_to_array.py"

dpkg-deb --build "$PKG_DIR" "$OUT_DIR/conversor-image-array_1.0.0_all.deb"

echo "Pacote Debian gerado em: $OUT_DIR/conversor-image-array_1.0.0_all.deb"
