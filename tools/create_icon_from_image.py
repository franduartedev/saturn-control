from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
OUT_PATH = ASSETS_DIR / "saturn_icon.ico"
SOURCE_NAMES = [
    "icon_source.png",
    "icon_source.jpg",
    "icon_source.jpeg",
    "icon_source.webp",
]
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def find_source_image():
    for name in SOURCE_NAMES:
        path = ASSETS_DIR / name
        if path.exists():
            return path
    return None


def make_square_icon(source_path):
    image = Image.open(source_path).convert("RGBA")
    image = ImageOps.exif_transpose(image)

    size = max(image.size)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = ((size - image.width) // 2, (size - image.height) // 2)
    canvas.alpha_composite(image, offset)

    canvas.save(OUT_PATH, format="ICO", sizes=ICO_SIZES)
    print(f"Icono generado desde imagen: {source_path}")
    print(f"Salida: {OUT_PATH}")


def main():
    source = find_source_image()
    if not source:
        raise FileNotFoundError(
            "No encontre assets/icon_source.png, .jpg, .jpeg o .webp"
        )
    make_square_icon(source)


if __name__ == "__main__":
    main()
