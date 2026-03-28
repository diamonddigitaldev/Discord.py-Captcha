from __future__ import annotations

import asyncio
import io
import math
import random
import secrets
import string
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

from .errors import CaptchaError

@dataclass
class CaptchaImageData:
    image: bytes
    text: str

def _create_captcha_sync(length: int, blacklist: str) -> CaptchaImageData:
    chars = [c for c in string.ascii_letters + string.digits if c not in blacklist]

    # Create canvas
    width, height = 400, 250

    img = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Draw background lines
    coords: list[list[int]] = []
    for i in range(4):
        row = [round(random.random() * 80) + j * 80 for j in range(5)]
        if not (i % 2):
            random.shuffle(row)

        coords.append(row)

    for i in range(len(coords)):
        if not (i % 2):
            for j in range(len(coords[i])):
                if not i:
                    draw.line(
                        [(coords[i][j], 0), (coords[i + 1][j], height)],
                        fill="black",
                        width=4
                    )
                else:
                    draw.line(
                        [(0, coords[i][j]), (width, coords[i + 1][j])],
                        fill="black",
                        width=4
                    )

    # Draw background circles
    for _ in range(200):
        x = round(random.random() * 360) + 20
        y = round(random.random() * 360) + 20
        r = round(random.random() * 7) + 1

        draw.ellipse([x - r, y - r, x + r, y + r], fill="black")

    # Generate text
    text = "".join(secrets.choice(chars) for _ in range(length))

    # Calculate font size
    font_size = max(20, min(100, int(80 / (length / 7.5)) if length > 6 else 80))
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError:
        font = ImageFont.load_default()

    # Render text onto a temporary image, then rotate and paste
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    padding = 40
    txt_img = Image.new("RGBA", (text_width + padding, text_height + padding), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((padding // 2, padding // 2), text, fill="black", font=font)

    # Rotate
    angle = (random.random() - 0.5) * (180 / math.pi)
    txt_img = txt_img.rotate(angle, expand=True, resample=Image.BICUBIC)

    # Calculate paste position
    offset_x = round(random.random() * 100 - 50) + 200 - txt_img.width // 2
    offset_y = round(random.random() * (height / 4) - height / 8) + height // 2 - txt_img.height // 2
    offset_x = max(0, min(offset_x, width - txt_img.width))
    offset_y = max(0, min(offset_y, height - txt_img.height))

    img.paste(txt_img, (offset_x, offset_y), txt_img)

    # Draw foreground noise
    for _ in range(5000):
        r_val = random.randint(0, 255)
        g_val = random.randint(0, 255)
        b_val = random.randint(0, 255)

        x = round(random.random() * width)
        y = round(random.random() * height)
        r = random.random() * 2

        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=(r_val, g_val, b_val, 0xa0)
        )

    # Export as PNG bytes
    with io.BytesIO() as buf:
        img.save(buf, format="PNG")
        return CaptchaImageData(image=buf.getvalue(), text=text)

async def create_captcha(length: int = 6, blacklist: str = "") -> CaptchaImageData:
    if not isinstance(length, int) or length < 1:
        raise CaptchaError("Length must be an integer greater than 0.")
    
    if not isinstance(blacklist, str):
        raise CaptchaError("Blacklist must be a string.")
    
    if blacklist and not all(c.isalnum() for c in blacklist):
        raise CaptchaError("Blacklist must only contain alphanumeric characters.")

    pool = [c for c in string.ascii_letters + string.digits if c not in blacklist]
    if not pool:
        raise CaptchaError("Blacklist excludes all available characters.")

    return await asyncio.to_thread(_create_captcha_sync, length, blacklist)
