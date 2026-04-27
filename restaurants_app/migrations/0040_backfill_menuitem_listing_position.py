"""
Data migration: assign a sensible listing_position to every existing MenuItem,
so the new ordering field has meaningful values for already-created data.

Strategy: per section, order items alphabetically by name (matching the
previous Meta.ordering behaviour) and assign incrementing positions 0..N-1.
Result: existing data renders in the same visual order it did before this
PR. Reordering becomes possible going forward but doesn't disrupt the past.

Each section's backfill is in its own transaction. If one section's backfill
hits an unexpected error, that section rolls back but the rest of the
migration continues -- and the deploy log will show exactly which section
failed. This is a deliberate trade-off versus the alternative of one
giant transaction (atomic-everything-or-nothing): we'd rather have most
sections healed and one logged failure than a total rollback.
"""
from django.db import migrations, transaction


def backfill_listing_position(apps, schema_editor):
    MenuSection = apps.get_model('restaurants_app', 'MenuSection')
    MenuItem = apps.get_model('restaurants_app', 'MenuItem')

    section_ids = list(MenuSection.objects.values_list('id', flat=True))
    total_items = 0
    total_sections = 0
    failed_sections = []

    for section_id in section_ids:
        try:
            with transaction.atomic():
                items = list(
                    MenuItem.objects.filter(section_id=section_id).order_by('name', 'time_created')
                )
                if not items:
                    continue
                for index, item in enumerate(items):
                    if item.listing_position != index:
                        item.listing_position = index
                        item.save(update_fields=['listing_position'])
                    total_items += 1
                total_sections += 1
        except Exception as e:
            print(f'[0040 migration] FAILED on section_id={section_id}: {e}')
            failed_sections.append(str(section_id))

    print(f'[0040 migration] backfilled {total_items} items across {total_sections} sections')
    if failed_sections:
        print(f'[0040 migration] {len(failed_sections)} section(s) failed: {failed_sections}')


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants_app', '0039_menuitem_listing_position'),
    ]

    operations = [
        migrations.RunPython(backfill_listing_position, migrations.RunPython.noop),
    ]
