import logging
import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)


def optimize_image(image_field, max_width=600, max_height=600, quality=75, force=False):
    """
    Resizes and compresses an image, writing it back as WebP.

    By default the function skips images that already fit within
    max_width x max_height. Pass force=True to re-encode regardless of
    size (used by the reoptimise_menu_images management command to
    migrate existing JPEGs to WebP).

    Args:
        image_field: Django ImageField instance
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: WebP compression quality (1-100)
        force: If True, re-encode even when the image is already within bounds

    Returns:
        True if image was re-encoded, False if legitimately skipped
        (no image attached, or already within bounds and force=False).
        Exceptions propagate to the caller so failures aren't silently
        masked as skips.
    """
    if not image_field or not image_field.name:
        return False

    image_field.open()
    img = Image.open(image_field)

    original_width, original_height = img.size

    if not force and original_width <= max_width and original_height <= max_height:
        image_field.seek(0)
        return False

    if img.mode in ('RGBA', 'P', 'LA', 'CMYK'):
        img = img.convert('RGB')
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    img.thumbnail((max_width, max_height), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=quality, method=6)
    buffer.seek(0)

    # Use only the bare filename — image_field.save() will re-apply the
    # field's upload_to prefix. Passing the full stored name (which already
    # includes upload_to) would nest the file one directory deeper on every
    # call (menu_items/menu_items/foo.webp, then menu_items/menu_items/menu_items/...).
    name = os.path.basename(image_field.name)
    if '.' in name:
        name = name.rsplit('.', 1)[0] + '.webp'
    else:
        name = name + '.webp'

    image_field.save(
        name,
        InMemoryUploadedFile(
            buffer, 'ImageField', name, 'image/webp',
            buffer.getbuffer().nbytes, None
        ),
        save=False  # Don't trigger another model save
    )

    logger.info(
        "Optimized image: %s (%dx%d -> %dx%d)",
        name, original_width, original_height, img.size[0], img.size[1]
    )
    return True
