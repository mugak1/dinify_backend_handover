"""
Data migration: convert every Restaurant's branding_configuration['home']
from the old shape (bgColor / headerCase / headerShow / headerColor /
headerTextColor / headerShowName / viewMenuBgColor / headerFontWeight /
viewMenuTextColor) to the new shape (header_style / brand_color /
logo_display / tagline). The diner-app header refactor only consumes the
four new keys, so we drop everything else.

Mapping rules:
  - header_style: always 'solid' for existing rows
  - brand_color: old headerColor if non-empty, else '#171717'
  - logo_display: 'logo_only' if old headerShow == 'logo',
                  else 'name_only' (covers 'name' and the buggy default)
  - tagline:     ''

Idempotent: a row that already has exactly the four new keys (and no
old keys) is left untouched. Forward-only -- no production restaurants
exist, so reverse is a no-op.
"""
from django.db import migrations


NEW_KEYS = {'header_style', 'brand_color', 'logo_display', 'tagline'}


def migrate_branding_shape(apps, schema_editor):
    Restaurant = apps.get_model('restaurants_app', 'Restaurant')

    migrated = 0
    skipped = 0

    for restaurant in Restaurant.objects.all():
        config = restaurant.branding_configuration or {}
        home = config.get('home') or {}

        if set(home.keys()) == NEW_KEYS:
            skipped += 1
            continue

        old_header_color = home.get('headerColor')
        brand_color = old_header_color if old_header_color else '#171717'

        old_header_show = home.get('headerShow')
        if old_header_show == 'logo':
            logo_display = 'logo_only'
        elif old_header_show == 'name':
            logo_display = 'name_only'
        else:
            logo_display = 'name_only'

        config['home'] = {
            'header_style': 'solid',
            'brand_color': brand_color,
            'logo_display': logo_display,
            'tagline': '',
        }
        restaurant.branding_configuration = config
        restaurant.save(update_fields=['branding_configuration'])
        migrated += 1

    print(f'[0041 migration] migrated {migrated} restaurants, skipped {skipped} already-new')


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants_app', '0040_backfill_menuitem_listing_position'),
    ]

    operations = [
        migrations.RunPython(migrate_branding_shape, migrations.RunPython.noop),
    ]
