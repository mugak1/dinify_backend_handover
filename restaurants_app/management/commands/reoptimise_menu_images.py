import logging

from django.core.management.base import BaseCommand

from restaurants_app.models import MenuItem
from restaurants_app.utils.image_optimizer import optimize_image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Re-optimise existing MenuItem images, converting them to WebP at the '
        'current optimize_image() defaults. Safe to run repeatedly.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Log what would change without writing to DB or storage',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Process at most N items (useful for staged rollout)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        qs = MenuItem.objects.exclude(image='').exclude(image__isnull=True)
        if limit is not None:
            qs = qs[:limit]

        total_known = qs.count() if limit is None else min(qs.count(), limit)
        suffix = ' (dry-run)' if dry_run else ''
        self.stdout.write(
            f'Processing up to {total_known} menu item images{suffix}...'
        )

        processed = 0
        succeeded = 0
        failed = 0
        skipped = 0

        for item in qs.iterator():
            processed += 1
            try:
                if dry_run:
                    self.stdout.write(
                        f'Would re-optimise item {item.id} ({item.image.name})'
                    )
                    continue

                if optimize_image(item.image, force=True):
                    item.save(update_fields=['image'])
                    succeeded += 1
                else:
                    skipped += 1
            except Exception as e:
                failed += 1
                self.stderr.write(f'Failed for item {item.id}: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'Done{suffix}: processed={processed}, succeeded={succeeded}, '
            f'failed={failed}, skipped={skipped}'
        ))
