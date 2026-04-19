"""
Data migration: heal JSONField values that were saved as JSON-encoded strings
due to the multipart/form-data parsing bug on SerializerPutMenuItem and
SerializerPutMenuSection. For each affected row, parse the string back into
its intended list/dict and re-save.
"""
import json

from django.db import migrations, transaction


MENUITEM_FIELDS = [
    'options',
    'allergens',
    'tags',
    'discount_details',
    'extras_applicable',
]
MENUSECTION_FIELDS = ['schedules']


def _heal(apps, model_label, field_names):
    Model = apps.get_model('restaurants_app', model_label)

    planned = []
    for row in Model.objects.all().iterator():
        row_changes = {}
        for field_name in field_names:
            value = getattr(row, field_name)
            if isinstance(value, str):
                try:
                    row_changes[field_name] = json.loads(value)
                except json.JSONDecodeError:
                    continue
        if row_changes:
            planned.append((row.pk, row_changes))

    for pk, changes in planned[:5]:
        print(f"[0038 migration] {model_label} pk={pk} preview:")
        for field_name, new_value in changes.items():
            print(f"  {field_name}: str -> {type(new_value).__name__}")

    for pk, changes in planned:
        row = Model.objects.get(pk=pk)
        for field_name, new_value in changes.items():
            setattr(row, field_name, new_value)
        row.save(update_fields=list(changes.keys()))

    print(f"[0038 migration] {model_label}: fixed {len(planned)} row(s)")


def heal_corrupted(apps, schema_editor):
    with transaction.atomic():
        _heal(apps, 'MenuItem', MENUITEM_FIELDS)
        _heal(apps, 'MenuSection', MENUSECTION_FIELDS)


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants_app', '0037_add_calories_to_menuitem'),
    ]

    operations = [
        migrations.RunPython(heal_corrupted, migrations.RunPython.noop),
    ]
