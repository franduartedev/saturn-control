import math
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets"
OUT_PATH = OUT_DIR / "saturn_icon.ico"
SIZES = [16, 32, 48, 64, 128, 256]


def blend_pixel(pixel, color, alpha):
    r, g, b, a = pixel
    alpha = max(0.0, min(1.0, alpha))
    inv = 1.0 - alpha
    return (
        int(r * inv + color[0] * alpha),
        int(g * inv + color[1] * alpha),
        int(b * inv + color[2] * alpha),
        int(max(a, color[3] * alpha)),
    )


def set_pixel(canvas, x, y, color, alpha=1.0):
    size = len(canvas)
    if 0 <= x < size and 0 <= y < size:
        canvas[y][x] = blend_pixel(canvas[y][x], color, alpha)


def stroke_circle(canvas, cx, cy, radius, color, width):
    size = len(canvas)
    for y in range(size):
        for x in range(size):
            distance = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            delta = abs(distance - radius)
            if delta <= width:
                set_pixel(canvas, x, y, color, 1.0 - (delta / max(width, 1)))


def stroke_ellipse(canvas, cx, cy, rx, ry, angle, color, width):
    size = len(canvas)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    for y in range(size):
        for x in range(size):
            dx = x + 0.5 - cx
            dy = y + 0.5 - cy
            xr = dx * cos_a + dy * sin_a
            yr = -dx * sin_a + dy * cos_a
            value = math.sqrt((xr / rx) ** 2 + (yr / ry) ** 2)
            delta = abs(value - 1.0) * min(rx, ry)
            if delta <= width:
                set_pixel(canvas, x, y, color, 1.0 - (delta / max(width, 1)))


def fill_glow(canvas, cx, cy, radius, color):
    size = len(canvas)
    for y in range(size):
        for x in range(size):
            distance = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if distance <= radius:
                alpha = (1.0 - distance / radius) * 0.5
                set_pixel(canvas, x, y, color, alpha)


def draw_icon(size):
    canvas = [[(0, 0, 0, 0) for _ in range(size)] for _ in range(size)]
    cx = cy = size / 2
    cyan = (22, 201, 255, 255)
    blue = (9, 113, 255, 255)
    white = (235, 248, 255, 255)

    fill_glow(canvas, cx, cy, size * 0.48, (0, 90, 255, 150))
    stroke_ellipse(canvas, cx, cy, size * 0.42, size * 0.17, -0.36, cyan, max(1.0, size * 0.035))
    stroke_circle(canvas, cx, cy, size * 0.24, white, max(1.0, size * 0.032))
    stroke_circle(canvas, cx, cy, size * 0.31, blue, max(1.0, size * 0.018))
    stroke_ellipse(canvas, cx, cy, size * 0.48, size * 0.19, -0.36, blue, max(1.0, size * 0.018))

    star_positions = [(0.67, 0.24), (0.77, 0.63), (0.29, 0.28)]
    for sx, sy in star_positions:
        star_size = max(1, int(size * 0.025))
        px = int(size * sx)
        py = int(size * sy)
        for offset in range(-star_size, star_size + 1):
            set_pixel(canvas, px + offset, py, white, 0.9)
            set_pixel(canvas, px, py + offset, white, 0.9)

    return canvas


def canvas_to_dib(canvas):
    size = len(canvas)
    header = struct.pack(
        "<IIIHHIIIIII",
        40,
        size,
        size * 2,
        1,
        32,
        0,
        size * size * 4,
        0,
        0,
        0,
        0,
    )
    pixels = bytearray()
    for row in reversed(canvas):
        for r, g, b, a in row:
            pixels.extend([b, g, r, a])
    mask_row_size = ((size + 31) // 32) * 4
    mask = bytes(mask_row_size * size)
    return header + bytes(pixels) + mask


def write_ico(images):
    count = len(images)
    header = struct.pack("<HHH", 0, 1, count)
    entries = bytearray()
    data = bytearray()
    offset = 6 + count * 16

    for size, image_data in images:
        width_byte = 0 if size == 256 else size
        height_byte = 0 if size == 256 else size
        entries.extend(
            struct.pack(
                "<BBBBHHII",
                width_byte,
                height_byte,
                0,
                0,
                1,
                32,
                len(image_data),
                offset,
            )
        )
        data.extend(image_data)
        offset += len(image_data)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(header + bytes(entries) + bytes(data))


def main():
    images = [(size, canvas_to_dib(draw_icon(size))) for size in SIZES]
    write_ico(images)
    print(f"Icono generado: {OUT_PATH}")


if __name__ == "__main__":
    main()
