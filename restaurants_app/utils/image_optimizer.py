import logging
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
        True if image was re-encoded, False if skipped or on failure
    """
    try:
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

        name = image_field.name
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

    except Exception as e:
        logger.error("Image optimization failed: %s", e)
        return False
