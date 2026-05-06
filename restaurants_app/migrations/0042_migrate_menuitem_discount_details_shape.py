"""
Data migration: convert MenuItem.discount_details from the pre-fix buggy shape
to the canonical shape documented in restaurants_app/models.py:234-242.

Pre-fix buggy shape (written by the old item-form-dialog save handler):
  {
    discount_type, discount_amount,         # discount_amount = FINAL price
    raw_discount_value, raw_discount_type,  # the user's actual input
    recurring_days, start_date, end_date, start_time, end_time
  }

Canonical shape:
  {
    discount_type:        'percentage' | 'fixed',
    discount_percentage:  0..100 (percentage to subtract from primary_price),
    discount_amount:      UGX amount to subtract from primary_price,
    recurring_days, start_date, end_date, start_time, end_time
  }

Heuristic: any row whose discount_details dict contains 'raw_discount_value' or
'raw_discount_type' is rewritten. Rows without those keys are either canonical
already or carry no discount and are skipped (idempotent on re-run).

discounted_price is recomputed from the canonical fields so the
con_orders.py:170 fast path stays consistent. Reverse is a no-op (data is
recoverable from the canonical fields).
"""
from decimal import Decimal, ROUND_HALF_UP
from django.db import migrations


BUGGY_KEYS = ('raw_discount_value', 'raw_discount_type')


def _to_decimal(value):
    """Coerce arbitrary JSON value to Decimal via str (avoids float drift)."""
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal('0')


def _quantize_money(value):
    """Round to 2 decimal places, clamp at zero."""
    if value < 0:
        return Decimal('0.00')
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def migrate_discount_shape(apps, schema_editor):
    MenuItem = apps.get_model('restaurants_app', 'MenuItem')

    migrated = 0
    skipped = 0

    for item in MenuItem.objects.iterator(chunk_size=500):
        details = item.discount_details or {}
        if not isinstance(details, dict):
            skipped += 1
            continue
        if not any(k in details for k in BUGGY_KEYS):
            skipped += 1
            continue

        raw_value = _to_decimal(details.get('raw_discount_value', 0))
        raw_type = (
            details.get('raw_discount_type')
            or details.get('discount_type')
            or 'fixed'
        )

        primary = _to_decimal(item.primary_price or 0)

        if raw_type == 'percentage':
            pct = raw_value
            amt = Decimal('0')
            new_discounted = _quantize_money(
                primary * (Decimal('1') - pct / Decimal('100'))
            )
        else:
            pct = Decimal('0')
            amt = raw_value
            new_discounted = _quantize_money(primary - amt)

        item.discount_details = {
            'discount_type': raw_type,
            'discount_percentage': float(pct),
            'discount_amount': float(amt),
            'recurring_days': details.get('recurring_days', []),
            'start_date': details.get('start_date', ''),
            'end_date': details.get('end_date', ''),
            'start_time': details.get('start_time', ''),
            'end_time': details.get('end_time', ''),
        }
        item.discounted_price = new_discounted
        item.save(update_fields=['discount_details', 'discounted_price'])
        migrated += 1

    print(f'[0042 migration] migrated {migrated} menu items, skipped {skipped}')


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants_app', '0041_migrate_branding_configuration_shape'),
    ]

    operations = [
        migrations.RunPython(migrate_discount_shape, migrations.RunPython.noop),
    ]
