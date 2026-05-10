import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from restaurants_app.models import MenuItem
from restaurants_app.utils.image_optimizer import generate_thumbnail

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate image_thumbnail for MenuItems that have image but no thumbnail'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would be done without writing changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        items = (
            MenuItem.objects
            .exclude(image='').exclude(image__isnull=True)
            .filter(Q(image_thumbnail='') | Q(image_thumbnail__isnull=True))
        )
        total = items.count()
        self.stdout.write(f'Processing {total} menu items needing thumbnails...')

        generated = 0
        for item in items.iterator():
            try:
                if generate_thumbnail(item.image, item.image_thumbnail):
                    if not dry_run:
                        item.save(update_fields=['image_thumbnail'])
                    generated += 1
            except Exception as e:
                self.stderr.write(f'Failed for item {item.id}: {e}')

        verb = 'Would generate' if dry_run else 'Generated'
        self.stdout.write(self.style.SUCCESS(f'{verb} {generated} thumbnails'))
