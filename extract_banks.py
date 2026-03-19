import sys
import glob
from PIL import Image

def decode_chr(chr_data):
    """
    Decodes a standard NES 8x8 sprite from 16 bytes of CHR data.
    Returns a list of 64 integers (0-3) representing color indices.
    """
    pixels = [0] * 64
    for y in range(8):
        plane0 = chr_data[y]
        plane1 = chr_data[y + 8]
        for x in range(8):
            bit0 = (plane0 >> (7 - x)) & 1
            bit1 = (plane1 >> (7 - x)) & 1
            pixels[y * 8 + x] = (bit1 << 1) | bit0
    return pixels

def extract_bank(filepath, outpath):
    """
    Extracts an entire 4KB CHR bank (256 tiles) into a 16x16 grid image.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    # NES palette approximation (arbitrary grayscale/colors for visibility)
    palette = [
        (0, 0, 0, 255),        # Black
        (85, 85, 85, 255),     # Dark Gray
        (170, 170, 170, 255),  # Light Gray
        (255, 255, 255, 255)   # White
    ]

    img_w = 16 * 8
    img_h = 16 * 8
    img = Image.new('RGBA', (img_w, img_h))
    pixels = img.load()

    for tile_index in range(256):
        if (tile_index + 1) * 16 > len(data):
            break

        chr_block = data[tile_index * 16 : (tile_index + 1) * 16]
        decoded = decode_chr(chr_block)

        tile_x = (tile_index % 16) * 8
        tile_y = (tile_index // 16) * 8

        for y in range(8):
            for x in range(8):
                color_idx = decoded[y * 8 + x]
                pixels[tile_x + x, tile_y + y] = palette[color_idx]

    img.save(outpath)
    print(f"Saved bank to {outpath}")

if __name__ == "__main__":
    import os
    os.makedirs('web_ui/banks', exist_ok=True)
    banks = sorted(glob.glob('original_files/CHR_Bank*.bin'))
    for bank in banks:
        filename = os.path.basename(bank)
        outname = f"web_ui/banks/{filename.replace('.bin', '.png')}"
        extract_bank(bank, outname)
