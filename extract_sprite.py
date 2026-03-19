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

def build_mac_sprite(data, tile_mapping, palette, img_w, img_h):
    """
    Constructs a sprite image using a specific layout of tiles from the CHR bank.
    tile_mapping is a list of (tx, ty, tile_index, flip_x, flip_y) tuples.
    """
    img = Image.new('RGBA', (img_w, img_h))
    pixels = img.load()

    for tx, ty, t_idx, flip_x, flip_y in tile_mapping:
        chr_block = data[t_idx * 16 : (t_idx + 1) * 16]
        if len(chr_block) < 16: continue

        decoded = decode_chr(chr_block)
        for y in range(8):
            for x in range(8):
                color_idx = decoded[y * 8 + x]
                px = (7 - x) if flip_x else x
                py = (7 - y) if flip_y else y
                pixels[tx * 8 + px, ty * 8 + py] = palette[color_idx]

    return img

if __name__ == "__main__":
    with open('original_files/CHR_Bank01A.bin', 'rb') as f:
        data = f.read()

    # Little Mac approximate palette
    palette = [
        (0, 0, 0, 0),        # Transparent
        (0, 0, 0, 255),      # Black Outline
        (255, 175, 128, 255),# Skin
        (0, 255, 0, 255)     # Green gloves/shorts
    ]

    # We will build a simple spritesheet with two frames.
    # Mac idle frame (approximate tile indices from CHR_Bank01A/01B)
    mac_idle = [
        (1, 0, 0x1A, False, False), # Head L
        (2, 0, 0x1B, False, False), # Head R
        (0, 1, 0x18, False, False), # Shoulder L
        (1, 1, 0x2A, False, False), # Torso UL
        (2, 1, 0x2B, False, False), # Torso UR
        (3, 1, 0x19, False, False), # Shoulder R
        (0, 2, 0x01, False, False), # Glove L
        (1, 2, 0x3A, False, False), # Torso LL
        (2, 2, 0x3B, False, False), # Torso LR
        (3, 2, 0x00, True, False),  # Glove R (flipped)
        (1, 3, 0x2E, False, False), # Legs L
        (2, 3, 0x2E, True, False)   # Legs R (flipped)
    ]

    # Mac punch frame
    mac_punch = [
        (1, 0, 0x1A, False, False), # Head L
        (2, 0, 0x1B, False, False), # Head R
        (0, 1, 0x18, False, False), # Shoulder L
        (1, 1, 0x2A, False, False), # Torso UL
        (2, 1, 0x2B, False, False), # Torso UR
        (3, 1, 0x30, False, False), # Extended Arm 1
        (4, 1, 0x31, False, False), # Extended Arm 2
        (0, 2, 0x01, False, False), # Glove L
        (1, 2, 0x3A, False, False), # Torso LL
        (2, 2, 0x3B, False, False), # Torso LR
        (1, 3, 0x2E, False, False), # Legs L
        (2, 3, 0x2E, True, False)   # Legs R (flipped)
    ]

    img_idle = build_mac_sprite(data, mac_idle, palette, 32, 32)
    img_punch = build_mac_sprite(data, mac_punch, palette, 40, 32)

    # Create spritesheet
    spritesheet = Image.new('RGBA', (80, 32))
    spritesheet.paste(img_idle, (0, 0))
    spritesheet.paste(img_punch, (40, 0))
    spritesheet.save('web_ui/mac_spritesheet.png')

    print("Saved mac_spritesheet.png")
