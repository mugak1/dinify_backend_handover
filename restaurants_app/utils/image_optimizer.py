import logging
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)


def optimize_image(image_field, max_width=800, max_height=800, quality=80):
    """
    Resizes and compresses an image if it exceeds max dimensions.
    Converts to JPEG for consistent compression.
    Only processes if the image is actually larger than the max dimensions.

    Args:
        image_field: Django ImageField instance
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG compression quality (1-100)

    Returns:
        True if image was optimized, False if no optimization needed
    """
    try:
        if not image_field or not image_field.name:
            return False

        image_field.open()
        img = Image.open(image_field)

        original_width, original_height = img.size

        # Skip if already small enough
        if original_width <= max_width and original_height <= max_height:
            image_field.seek(0)
            return False

        # Convert RGBA/P to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize maintaining aspect ratio
        img.thumbnail((max_width, max_height), Image.LANCZOS)

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)

        # Generate new filename with .jpg extension
        name = image_field.name
        if '.' in name:
            name = name.rsplit('.', 1)[0] + '.jpg'

        # Save back to the field
        image_field.save(
            name,
            InMemoryUploadedFile(
                buffer, 'ImageField', name, 'image/jpeg',
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
