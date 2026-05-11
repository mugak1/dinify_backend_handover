"""
Idempotent data migration for the structured tag catalog (PR 1 of 5).

For every existing Restaurant:
  1. Seed the 14 system-default presets via get_or_create on
     (restaurant, name) — safe to re-run.
  2. Walk every MenuItem and, for each entry in the legacy
     `_legacy_tags` JSON list, find or create a matching RestaurantTag
     and link it via MenuItemTag. Case-insensitive matching against
     seeded presets; unmatched strings become custom descriptor tags
     coloured `gray` with no icon.

Reverse: best-effort — deletes catalog rows seeded as system presets
and removes the links populated here. The legacy `_legacy_tags` column
is left intact for an additional safety net (it was never touched).
"""
from django.db import migrations


# Mirrors restaurants_app.models.SYSTEM_PRESET_TAGS. Inlined here so
# the migration is stable against future edits of the model module.
SYSTEM_PRESET_TAGS = [
    {'name': 'Vegetarian',         'category': 'dietary',    'colour': 'green',   'icon': 'leaf',       'filterable': True},
    {'name': 'Vegan',              'category': 'dietary',    'colour': 'emerald', 'icon': 'sprout',     'filterable': True},
    {'name': 'Halal',              'category': 'dietary',    'colour': 'green',   'icon': 'moon-star',  'filterable': True},
    {'name': 'Gluten-Free',        'category': 'dietary',    'colour': 'amber',   'icon': 'wheat-off',  'filterable': True},
    {'name': 'Dairy-Free',         'category': 'dietary',    'colour': 'cyan',    'icon': 'milk-off',   'filterable': True},
    {'name': 'Contains Gluten',    'category': 'allergen',   'colour': 'amber',   'icon': 'wheat',      'filterable': True},
    {'name': 'Contains Dairy',     'category': 'allergen',   'colour': 'blue',    'icon': 'milk',       'filterable': True},
    {'name': 'Contains Nuts',      'category': 'allergen',   'colour': 'orange',  'icon': 'nut',        'filterable': True},
    {'name': 'Contains Eggs',      'category': 'allergen',   'colour': 'yellow',  'icon': 'egg',        'filterable': True},
    {'name': 'Contains Fish',      'category': 'allergen',   'colour': 'cyan',    'icon': 'fish',       'filterable': True},
    {'name': 'Contains Shellfish', 'category': 'allergen',   'colour': 'rose',    'icon': 'shell',      'filterable': True},
    {'name': 'Contains Soy',       'category': 'allergen',   'colour': 'green',   'icon': 'bean',       'filterable': True},
    {'name': 'Spicy',              'category': 'descriptor', 'colour': 'red',     'icon': 'flame',      'filterable': False},
    {'name': "Chef's Special",     'category': 'descriptor', 'colour': 'purple',  'icon': 'award',      'filterable': False},
]


def seed_and_backfill(apps, schema_editor):
    Restaurant = apps.get_model('restaurants_app', 'Restaurant')
    MenuItem = apps.get_model('restaurants_app', 'MenuItem')
    RestaurantTag = apps.get_model('restaurants_app', 'RestaurantTag')
    MenuItemTag = apps.get_model('restaurants_app', 'MenuItemTag')

    seeded_count = 0
    linked_count = 0
    custom_created_count = 0

    for restaurant in Restaurant.objects.iterator(chunk_size=200):
        # 1) Seed the 14 system-default presets idempotently.
        for index, preset in enumerate(SYSTEM_PRESET_TAGS, start=1):
            _, created = RestaurantTag.objects.get_or_create(
                restaurant=restaurant,
                name=preset['name'],
                defaults={
                    'category': preset['category'],
                    'colour': preset['colour'],
                    'icon': preset['icon'],
                    'filterable': preset['filterable'],
                    'display_order': index,
                    'is_system_preset': True,
                },
            )
            if created:
                seeded_count += 1

        # 2) Backfill MenuItem links from the legacy JSON column.
        items = MenuItem.objects.filter(section__restaurant=restaurant)
        for item in items.iterator(chunk_size=500):
            legacy = item._legacy_tags or []
            if not isinstance(legacy, list) or not legacy:
                continue

            for raw in legacy:
                value = (raw or '').strip() if isinstance(raw, str) else ''
                if not value:
                    continue

                tag = RestaurantTag.objects.filter(
                    restaurant=restaurant,
                    name__iexact=value,
                ).first()
                if tag is None:
                    # Unmatched legacy string -> custom descriptor tag.
                    tag = RestaurantTag.objects.create(
                        restaurant=restaurant,
                        name=value,
                        category='descriptor',
                        colour='gray',
                        icon=None,
                        filterable=False,
                        display_order=0,
                        is_system_preset=False,
                    )
                    custom_created_count += 1

                _, link_created = MenuItemTag.objects.get_or_create(
                    menu_item=item,
                    tag=tag,
                )
                if link_created:
                    linked_count += 1

    print(
        f'[0045 migration] seeded={seeded_count} presets, '
        f'custom={custom_created_count}, linked={linked_count}'
    )


def reverse_backfill(apps, schema_editor):
    RestaurantTag = apps.get_model('restaurants_app', 'RestaurantTag')
    MenuItemTag = apps.get_model('restaurants_app', 'MenuItemTag')
    MenuItemTag.objects.all().delete()
    RestaurantTag.objects.filter(is_system_preset=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants_app', '0044_create_restaurant_tag_catalog'),
    ]

    operations = [
        migrations.RunPython(seed_and_backfill, reverse_backfill),
    ]
