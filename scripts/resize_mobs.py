#!/usr/bin/env python3
"""
Resize images from `mob/` into `web/mob_images/` as 128x128 PNG thumbnails.
Preserves aspect ratio and centers image on transparent background.
"""
import os
from PIL import Image

SRC_DIR = 'mob'
DST_DIR = 'web/mob_images'
SIZE = (128, 128)

os.makedirs(DST_DIR, exist_ok=True)

for fn in sorted(os.listdir(SRC_DIR)):
    if not fn.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
        continue
    src = os.path.join(SRC_DIR, fn)
    base, _ = os.path.splitext(fn)
    dst = os.path.join(DST_DIR, base + '.png')
    try:
        with Image.open(src) as im:
            im = im.convert('RGBA')
            im.thumbnail(SIZE, Image.LANCZOS)
            # create background and paste centered
            bg = Image.new('RGBA', SIZE, (0, 0, 0, 0))
            x = (SIZE[0] - im.width) // 2
            y = (SIZE[1] - im.height) // 2
            bg.paste(im, (x, y), im)
            bg.save(dst, format='PNG')
            print('Saved', dst)
    except Exception as e:
        print('Failed', src, e)
