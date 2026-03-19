import sys
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

def extract_sprite(filepath, outpath, tile_index=0, width_tiles=2, height_tiles=4):
    """
    Extracts a rectangular sprite from a CHR bank.
    width_tiles and height_tiles specify how many 8x8 blocks make up the sprite.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    # NES palette approximation (just arbitrary colors for demonstration)
    palette = [
        (0, 0, 0, 0),        # Transparent
        (255, 100, 100, 255),# Color 1
        (100, 255, 100, 255),# Color 2
        (255, 255, 255, 255) # Color 3
    ]

    img_w = width_tiles * 8
    img_h = height_tiles * 8
    img = Image.new('RGBA', (img_w, img_h))

    pixels = img.load()

    # We will just guess the layout: often sprites are stored sequentially.
    # Let's read width*height tiles starting from tile_index.
    for ty in range(height_tiles):
        for tx in range(width_tiles):
            t_idx = tile_index + (ty * width_tiles + tx)
            chr_block = data[t_idx * 16 : (t_idx + 1) * 16]
            if len(chr_block) < 16:
                break

            decoded = decode_chr(chr_block)
            for y in range(8):
                for x in range(8):
                    color_idx = decoded[y * 8 + x]
                    pixels[tx * 8 + x, ty * 8 + y] = palette[color_idx]

    img.save(outpath)
    print(f"Saved sprite to {outpath}")

if __name__ == "__main__":
    # We'll just grab an arbitrary set of tiles from CHR_Bank000 to demonstrate
    # we can pull assets from the original assembly files.
    # In a full port, we'd map this perfectly.
    extract_sprite('original_files/CHR_Bank000.bin', 'web_ui/sprite.png', tile_index=32, width_tiles=2, height_tiles=4)
