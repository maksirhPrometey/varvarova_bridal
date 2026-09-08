from __future__ import annotations

import io
import logging

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger(__name__)

TONES: dict[str, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]] = {
    'ivory': ((244, 238, 228), (226, 216, 200), (92, 78, 66)),
    'white': ((248, 248, 246), (230, 230, 226), (64, 64, 62)),
    'champagne': ((234, 220, 196), (206, 184, 152), (88, 68, 48)),
    'blush': ((238, 220, 218), (216, 186, 184), (92, 58, 58)),
    'black': ((22, 22, 22), (44, 42, 40), (236, 230, 222)),
    'red': ((78, 20, 28), (122, 34, 42), (244, 232, 228)),
    'emerald': ((16, 42, 36), (28, 72, 58), (228, 236, 228)),
    'navy': ((16, 24, 42), (32, 44, 72), (228, 230, 238)),
}

_BANNER = ((28, 24, 22), (72, 58, 50), (244, 236, 226))


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        '/System/Library/Fonts/Supplemental/Georgia.ttf',
        '/Library/Fonts/Georgia.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    width, height = size
    base = Image.new('RGB', size, top)
    overlay = Image.new('RGB', size, bottom)
    mask = Image.linear_gradient('L').resize(size)
    return Image.composite(overlay, base, mask)


def _mix(left: tuple[int, int, int], right: tuple[int, int, int], weight: float) -> tuple[int, int, int]:
    return tuple(int(left[i] + (right[i] - left[i]) * weight) for i in range(3))


def _gown(size: tuple[int, int], fill: tuple[int, int, int, int], kind: int) -> Image.Image:
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if kind == 0:
        draw.ellipse((360, 70, 600, 340), fill=fill)
        draw.ellipse((300, 280, 660, 780), fill=fill)
        draw.polygon([(220, 700), (740, 700), (860, 1200), (100, 1200)], fill=fill)
    elif kind == 1:
        draw.ellipse((80, -40, 520, 420), fill=fill)
        draw.ellipse((40, 280, 700, 980), fill=fill)
    elif kind == 2:
        draw.ellipse((-80, 220, 1040, 720), fill=fill)
        draw.ellipse((120, 640, 840, 1280), fill=fill)
    else:
        draw.ellipse((520, 90, 820, 400), fill=fill)
        draw.ellipse((440, 320, 900, 820), fill=fill)
        draw.polygon([(380, 740), (940, 680), (1020, 1200), (280, 1200)], fill=fill)
    return layer.filter(ImageFilter.GaussianBlur(32))


def render_portrait(label: str, tone: str, *, variant: int = 0) -> bytes:
    del label
    top, bottom, _ink = TONES.get(tone, TONES['ivory'])
    kind = variant % 4
    if kind in (1, 2):
        top, bottom = bottom, top
    base = _gradient((960, 1200), top, bottom).convert('RGBA')
    fill = (*_mix(top, bottom, 0.4), 88)
    composed = Image.alpha_composite(base, _gown((960, 1200), fill, kind))
    return _to_jpeg(composed.convert('RGB'))


def render_banner() -> bytes:
    width, height = 1920, 1080
    left = Image.new('RGB', (width, height), (24, 20, 18))
    right = Image.new('RGB', (width, height), (86, 68, 56))
    mask = Image.linear_gradient('L').rotate(90, expand=True).resize((width, height))
    base = Image.composite(right, left, mask).convert('RGBA')

    figure = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(figure)
    draw.ellipse((1188, 96, 1488, 420), fill=(240, 228, 212, 70))
    draw.ellipse((1104, 300, 1572, 780), fill=(232, 214, 196, 92))
    draw.polygon(
        [(940, 580), (1720, 580), (1840, 1080), (820, 1080)],
        fill=(222, 200, 178, 110),
    )
    figure = figure.filter(ImageFilter.GaussianBlur(36))
    return _to_jpeg(Image.alpha_composite(base, figure).convert('RGB'))


def render_cover(label: str, tone: str = 'ivory') -> bytes:
    top, bottom, ink = TONES.get(tone, TONES['ivory'])
    image = _gradient((1400, 900), top, bottom)
    draw = ImageDraw.Draw(image)
    font = _font(48)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((1400 - text_w) / 2, 400), label, fill=ink, font=font)
    return _to_jpeg(image)


def _to_jpeg(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=84, optimize=True)
    return buffer.getvalue()


def as_file(data: bytes, name: str) -> ContentFile:
    return ContentFile(data, name=name)
