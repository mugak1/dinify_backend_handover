# Generated for the structured tag catalog (PR 1 of 5).
#
# Introduces RestaurantTag (per-restaurant catalog) and MenuItemTag
# (join table) and adds a `tags` ManyToMany on MenuItem through that
# join. The existing MenuItem.tags JSON column is renamed to
# `_legacy_tags` at the Python level only — the DB column keeps its
# original name (`tags`) so production data is untouched. A follow-up
# PR will drop the legacy column once the new schema is verified.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("restaurants_app", "0043_migrate_menuitem_allergens_to_tags"),
    ]

    operations = [
        # 1) Rename the legacy free-form JSON column at the Python
        # level only. The DB column keeps the name `tags` via
        # db_column so existing rows are untouched.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name="menuitem",
                    old_name="tags",
                    new_name="_legacy_tags",
                ),
                migrations.AlterField(
                    model_name="menuitem",
                    name="_legacy_tags",
                    field=models.JSONField(
                        blank=True, db_column="tags", default=list
                    ),
                ),
            ],
            database_operations=[],
        ),
        # 2) Per-restaurant tag catalog.
        migrations.CreateModel(
            name="RestaurantTag",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("time_created", models.DateTimeField(auto_now_add=True)),
                ("time_last_updated", models.DateTimeField(auto_now=True)),
                ("time_deleted", models.DateTimeField(blank=True, null=True)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "deletion_reason",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("archived", models.BooleanField(default=False)),
                ("vacuumed", models.BooleanField(default=False)),
                ("eod_last_date", models.DateField(db_index=True, null=True)),
                ("eod_record_date", models.DateField(db_index=True, null=True)),
                ("name", models.CharField(max_length=50)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("allergen", "Allergen"),
                            ("dietary", "Dietary"),
                            ("descriptor", "Descriptor"),
                        ],
                        max_length=20,
                    ),
                ),
                ("icon", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "colour",
                    models.CharField(
                        choices=[
                            ("gray", "Gray"),
                            ("red", "Red"),
                            ("orange", "Orange"),
                            ("amber", "Amber"),
                            ("yellow", "Yellow"),
                            ("green", "Green"),
                            ("emerald", "Emerald"),
                            ("cyan", "Cyan"),
                            ("blue", "Blue"),
                            ("purple", "Purple"),
                            ("rose", "Rose"),
                        ],
                        default="gray",
                        max_length=20,
                    ),
                ),
                ("filterable", models.BooleanField(default=True)),
                ("display_order", models.IntegerField(default=0)),
                ("is_system_preset", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "deleted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_deleted_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "restaurant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tag_catalog",
                        to="restaurants_app.restaurant",
                    ),
                ),
            ],
            options={
                "db_table": "restaurant_tags",
                "ordering": ["display_order", "name"],
                "unique_together": {("restaurant", "name")},
            },
        ),
        # 3) Join table linking MenuItem to RestaurantTag.
        migrations.CreateModel(
            name="MenuItemTag",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("time_created", models.DateTimeField(auto_now_add=True)),
                ("time_last_updated", models.DateTimeField(auto_now=True)),
                ("time_deleted", models.DateTimeField(blank=True, null=True)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "deletion_reason",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("archived", models.BooleanField(default=False)),
                ("vacuumed", models.BooleanField(default=False)),
                ("eod_last_date", models.DateField(db_index=True, null=True)),
                ("eod_record_date", models.DateField(db_index=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "deleted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_deleted_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "menu_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tag_links",
                        to="restaurants_app.menuitem",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="item_links",
                        to="restaurants_app.restauranttag",
                    ),
                ),
            ],
            options={
                "db_table": "menu_item_tags",
                "unique_together": {("menu_item", "tag")},
            },
        ),
        # 4) M2M relation on MenuItem through the join table.
        migrations.AddField(
            model_name="menuitem",
            name="tags",
            field=models.ManyToManyField(
                related_name="menu_items",
                through="restaurants_app.MenuItemTag",
                to="restaurants_app.restauranttag",
            ),
        ),
    ]
