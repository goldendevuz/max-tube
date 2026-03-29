import traceback
from django.contrib import admin
from django.utils.html import format_html
from django.db import models as dj_models
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from parler.admin import TranslatableAdmin
from dateutil.relativedelta import relativedelta

from apps.shared.admin import BaseAdmin
from .models import (
    Playlist,
    Video,
    Category,
    Channel
)


# ----------------------------
# Patch all models __str__ to always return string
# ----------------------------
def safe_str_method(original_str):
    def wrapped(self):
        try:
            val = original_str(self)
            return str(val) if val is not None else ""
        except Exception:
            return ""
    return wrapped


for model in [Playlist, Video, Category, Channel]:
    if hasattr(model, "__str__"):
        model.__str__ = safe_str_method(model.__str__)
    else:
        # If no __str__, add one returning empty string
        model.__str__ = lambda self: ""


# ----------------------------
# Helper functions
# ----------------------------
def get_translatable_fields(model):
    """
    Returns a list of field names that are translatable (Parler-safe).
    """
    if hasattr(model, "_parler_meta"):
        return list(model._parler_meta.get_all_fields())
    return []


def register_model(model):
    """
    Dynamically registers a model with the Django admin,
    handling both Translatable and non-Translatable models.
    """
    # ----------------------------
    # Prepare resource fields for import/export
    # ----------------------------
    resource_fields = {}
    for f in model._meta.fields:
        if isinstance(f, dj_models.ForeignKey):
            resource_fields[f.name] = fields.Field(
                column_name=f.name,
                attribute=f.name,
                widget=ForeignKeyWidget(f.related_model, 'id')
            )

    # Create dynamic resource class
    resource_class = type(
        f"{model.__name__}Resource",
        (resources.ModelResource,),
        {
            **resource_fields,
            "Meta": type("Meta", (), {"model": model})
        },
    )

    # ----------------------------
    # Determine admin base classes
    # ----------------------------
    is_translatable = hasattr(model, "_parler_meta")
    base_classes = (ImportExportModelAdmin, BaseAdmin)
    if is_translatable:
        base_classes = (TranslatableAdmin,) + base_classes

    # ----------------------------
    # Fields for admin display
    # ----------------------------
    translatable_fields = get_translatable_fields(model)
    non_translatable_fields = [
        f.name for f in model._meta.fields if f.name not in translatable_fields
    ]

    admin_attrs = {
        "resource_classes": [resource_class],
        "list_display": list(non_translatable_fields) + translatable_fields + [
            f"get_{f.name}" for f in model._meta.many_to_many
        ],
        "list_filter": [
            f.name
            for f in model._meta.fields
            if f.get_internal_type()
            in ["BooleanField", "NullBooleanField", "DateField", "DateTimeField", "ForeignKey"]
        ],
        "search_fields": list(non_translatable_fields),
    }

    # ----------------------------
    # Add ManyToMany display methods
    # ----------------------------
    for f in model._meta.many_to_many:
        method_name = f"get_{f.name}"

        def make_m2m(field_name):
            def m2m(self, obj):
                items = getattr(obj, field_name).all()
                return ", ".join([str(i) for i in items[:5]]) + (" ..." if items.count() > 5 else "")
            m2m.short_description = field_name
            return m2m

        admin_attrs[method_name] = make_m2m(f.name)


    if is_translatable:
        for field in translatable_fields:
            admin_attrs["search_fields"].append(field)

    # ----------------------------
    # Add safe text preview methods
    # ----------------------------
    for f in model._meta.fields:
        if isinstance(f, dj_models.TextField):
            method_name = f"short_{f.name}"

            def make_preview(field_name):
                def preview(self, obj):
                    val = getattr(obj, field_name)
                    return (val[:47] + "...") if val else ""
                preview.short_description = field_name
                return preview

            admin_attrs[method_name] = make_preview(f.name)
            admin_attrs["list_display"].insert(0, method_name)

    # ----------------------------
    # Add safe image thumbnail methods
    # ----------------------------
    for f in model._meta.fields:
        if isinstance(f, dj_models.ImageField):
            method_name = f"show_{f.name}"

            def make_thumb(field_name):
                def thumb(self, obj):
                    val = getattr(obj, field_name)
                    if val and hasattr(val, "url"):
                        return format_html(
                            '<a href="{0}" target="_blank">'
                            '<img src="{0}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />'
                            "</a>",
                            val.url,
                        )
                    return "-"
                thumb.short_description = field_name
                return thumb

            admin_attrs[method_name] = make_thumb(f.name)
            admin_attrs["list_display"].append(method_name)

    # ----------------------------
    # Register admin class
    # ----------------------------
    admin_class = type(f"{model.__name__}Admin", base_classes, admin_attrs)
    admin.site.register(model, admin_class)


# ----------------------------
# Register all models
# ----------------------------
registered_models = [
    Playlist,
    Video,
    Category,
    Channel
]

for model in registered_models:
    try:
        register_model(model)
    except Exception as e:
        print(f"\n❌ Failed to register {model.__name__}: {e}")
        traceback.print_exc()


# ----------------------------
# Channel date update actions
# ----------------------------
@admin.action(description="Update selected channels' date for a month")
def update_channel_date_month(modeladmin, request, queryset):
    for obj in queryset:
        checkout = obj.checkout + relativedelta(months=1)
        obj.checkout = checkout
        obj.save()


@admin.action(description="Update selected channels' date for a week")
def update_channel_date_week(modeladmin, request, queryset):
    for obj in queryset:
        checkout = obj.checkout + relativedelta(weeks=1)
        obj.checkout = checkout
        obj.save()


@admin.action(description="Update selected channels' date for a day")
def update_channel_date_day(modeladmin, request, queryset):
    for obj in queryset:
        checkout = obj.checkout + relativedelta(days=1)
        obj.checkout = checkout
        obj.save()
