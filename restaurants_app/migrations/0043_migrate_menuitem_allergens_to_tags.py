"""
Data migration: move MenuItem.allergens contents into MenuItem.tags.

Background
----------
Until this PR the menu-item form's preset-tag picker wrote dietary tags
(e.g. "vegan", "spicy", "popular") into MenuItem.allergens. The diner UI
read MenuItem.allergens and rendered it under the heading "Dietary Info".
MenuItem.tags existed in the model but had zero UI consumers.

This migration corrects the model usage by moving every saved value out of
allergens and into tags, so the field whose name matches its purpose
("tags") is the one carrying the dietary-tag payload going forward.
MenuItem.allergens is left intact (zero'd out) for the future
allergen-warning feature.

Merge semantics
---------------
For each item:
  - If allergens is empty: skip.
  - Otherwise concat tags + allergens, deduplicating while preserving order
    (existing tags first, then allergens entries that aren't already in tags).
  - Write the merged list to tags, set allergens to [].

Reverse
-------
Best-effort reverse moves tags back to allergens. If an item had data in
both fields pre-forward-migration, that information is lost in the reverse
(both end up in allergens) -- acceptable for a rollback path on a UAT
dataset with no production restaurants onboarded.
"""
from django.db import migrations


def migrate_allergens_to_tags(apps, schema_editor):
    MenuItem = apps.get_model('restaurants_app', 'MenuItem')

    moved = 0
    skipped = 0

    for item in MenuItem.objects.iterator(chunk_size=500):
        allergens = item.allergens or []
        if not isinstance(allergens, list) or not allergens:
            skipped += 1
            continue

        existing_tags = item.tags or []
        if not isinstance(existing_tags, list):
            existing_tags = []

        merged = list(existing_tags)
        for value in allergens:
            if value not in merged:
                merged.append(value)

        item.tags = merged
        item.allergens = []
        item.save(update_fields=['tags', 'allergens'])
        moved += 1

    print(f'[0043 migration] moved {moved} menu items, skipped {skipped}')


def reverse_migrate(apps, schema_editor):
    MenuItem = apps.get_model('restaurants_app', 'MenuItem')

    for item in MenuItem.objects.iterator(chunk_size=500):
        tags = item.tags or []
        if not isinstance(tags, list) or not tags:
            continue
        item.allergens = list(tags)
        item.tags = []
        item.save(update_fields=['tags', 'allergens'])


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants_app', '0042_migrate_menuitem_discount_details_shape'),
    ]

    operations = [
        migrations.RunPython(migrate_allergens_to_tags, reverse_migrate),
    ]
