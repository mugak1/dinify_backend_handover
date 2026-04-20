from django.core.management.base import BaseCommand

from restaurants_app.models import MenuItem


class Command(BaseCommand):
    help = 'Inspect MenuItem fields (options, allergens, flags) for debugging'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, default='Classic Beef Burger')
        parser.add_argument(
            '--clean-allergens',
            action='store_true',
            help='Remove empty/whitespace entries from the allergens list and save.',
        )

    def handle(self, *args, **options):
        name = options['name']
        clean = options['clean_allergens']

        items = MenuItem.objects.filter(name__icontains=name)

        if not items.exists():
            self.stdout.write(f"No items found matching '{name}'")
            return

        for item in items:
            self.stdout.write(f"\n=== {item.name} (ID: {item.id}) ===")
            self.stdout.write(f"Section: {item.section.name}")
            self.stdout.write(f"Options type: {type(item.options)}")
            self.stdout.write(f"Options value: {item.options}")
            self.stdout.write(f"Allergens: {item.allergens}")
            self.stdout.write(f"Available: {item.available}")
            self.stdout.write(f"Approved: {item.approved}")
            self.stdout.write(f"Enabled: {item.enabled}")
            self.stdout.write(f"In stock: {item.in_stock}")

            if clean and item.allergens and any(
                not a or not str(a).strip() for a in item.allergens
            ):
                cleaned = [a for a in item.allergens if a and str(a).strip()]
                self.stdout.write(
                    f"Cleaning allergens: {item.allergens} -> {cleaned}"
                )
                item.allergens = cleaned
                item.save(update_fields=['allergens'])
                self.stdout.write(self.style.SUCCESS('Allergens cleaned and saved.'))
