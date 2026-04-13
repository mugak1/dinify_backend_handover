import logging

from django.core.management.base import BaseCommand

from restaurants_app.models import MenuItem, Restaurant, MenuSection
from restaurants_app.utils.image_optimizer import optimize_image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize all existing menu item, restaurant, and section images'

    def handle(self, *args, **options):
        # Menu items
        items = MenuItem.objects.exclude(image='').exclude(image__isnull=True)
        self.stdout.write(f'Processing {items.count()} menu item images...')
        optimized = 0
        for item in items.iterator():
            try:
                if optimize_image(item.image):
                    item.save(update_fields=['image'])
                    optimized += 1
            except Exception as e:
                self.stderr.write(f'Failed for item {item.id}: {e}')
        self.stdout.write(self.style.SUCCESS(f'Optimized {optimized} menu item images'))

        # Restaurant logos and covers
        restaurants = Restaurant.objects.all()
        self.stdout.write(f'Processing {restaurants.count()} restaurant images...')
        rest_optimized = 0
        for rest in restaurants.iterator():
            try:
                changed = False
                if rest.logo and optimize_image(rest.logo):
                    changed = True
                if rest.cover_photo and optimize_image(rest.cover_photo):
                    changed = True
                if changed:
                    rest.save()
                    rest_optimized += 1
            except Exception as e:
                self.stderr.write(f'Failed for restaurant {rest.id}: {e}')
        self.stdout.write(self.style.SUCCESS(f'Optimized {rest_optimized} restaurants'))

        # Section banners
        sections = MenuSection.objects.exclude(
            section_banner_image=''
        ).exclude(section_banner_image__isnull=True)
        self.stdout.write(f'Processing {sections.count()} section banner images...')
        section_optimized = 0
        for section in sections.iterator():
            try:
                if optimize_image(section.section_banner_image, max_width=1200, max_height=400):
                    section.save(update_fields=['section_banner_image'])
                    section_optimized += 1
            except Exception as e:
                self.stderr.write(f'Failed for section {section.id}: {e}')
        self.stdout.write(self.style.SUCCESS(f'Optimized {section_optimized} section banners'))

        self.stdout.write(self.style.SUCCESS('Done!'))
