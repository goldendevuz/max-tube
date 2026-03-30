from django.db import models
from django.conf import settings
from django_extensions.db.models import TimeStampedModel
from django.forms.models import model_to_dict
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings as dj_settings


# =====================================================
# 🔐 ENCRYPTION CORE
# =====================================================
fernet = Fernet(dj_settings.FIELD_ENCRYPTION_KEY)


def encrypt(value):
    if value is None:
        return value
    return fernet.encrypt(value.encode()).decode()


def decrypt(value):
    if value is None:
        return value
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception:
        return value


class EncryptedTextField(models.TextField):
    def from_db_value(self, value, expression, connection):
        return decrypt(value)

    def to_python(self, value):
        return decrypt(value)

    def get_prep_value(self, value):
        return encrypt(value)


class EncryptedCharField(models.CharField):
    def from_db_value(self, value, expression, connection):
        return decrypt(value)

    def to_python(self, value):
        return decrypt(value)

    def get_prep_value(self, value):
        return encrypt(value)


# =====================================================
# 🔍 HASH MIXIN (SEARCH)
# =====================================================
class HashMixin:
    HASH_FIELDS = []

    def generate_hash(self, value):
        return hashlib.sha256(value.encode()).hexdigest()

    def save(self, *args, **kwargs):
        for field in self.HASH_FIELDS:
            value = getattr(self, field, None)
            if value:
                setattr(self, f"{field}_hash", self.generate_hash(value))
            else:
                setattr(self, f"{field}_hash", None)
        super().save(*args, **kwargs)


# =====================================================
# 📜 AUDIT LOG
# =====================================================
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    model = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changes = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model} ({self.object_id}) - {self.action}"


# =====================================================
# 📜 AUDIT MIXIN
# =====================================================
class AuditMixin:

    def get_model_name(self):
        return self.__class__.__name__

    def get_changes(self, old, new):
        changes = {}
        for field, old_value in old.items():
            new_value = new.get(field)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
        return changes

    def save(self, *args, **kwargs):
        from apps.shared.utils.middleware import get_current_user
        user = get_current_user()

        if self.pk:
            old = self.__class__.objects.get(pk=self.pk)
            old_data = model_to_dict(old)
            super().save(*args, **kwargs)
            new_data = model_to_dict(self)

            changes = self.get_changes(old_data, new_data)

            if changes:
                AuditLog.objects.create(
                    user=user,
                    model=self.get_model_name(),
                    object_id=self.pk,
                    action="update",
                    changes=changes
                )
        else:
            super().save(*args, **kwargs)
            AuditLog.objects.create(
                user=user,
                model=self.get_model_name(),
                object_id=self.pk,
                action="create",
                changes=model_to_dict(self)
            )

    def delete(self, *args, **kwargs):
        from apps.shared.utils.middleware import get_current_user
        user = get_current_user()

        AuditLog.objects.create(
            user=user,
            model=self.get_model_name(),
            object_id=self.pk,
            action="delete",
            changes=model_to_dict(self)
        )

        super().delete(*args, **kwargs)


# =====================================================
# 📦 MODELS
# =====================================================
class Category(AuditMixin, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name or ""


class Channel(AuditMixin, HashMixin, TimeStampedModel):
    HASH_FIELDS = ["url"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    url = EncryptedTextField(unique=True, null=True, blank=True)
    url_hash = models.CharField(max_length=64, db_index=True, unique=True, null=True, blank=True)

    title = EncryptedCharField(max_length=255, null=True, blank=True)
    description = EncryptedTextField(null=True, blank=True)

    total_watch = models.PositiveSmallIntegerField(default=0)
    next_video = models.CharField(max_length=255, null=True, blank=True)
    has_new_video = models.BooleanField(default=False)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    checkout = models.DateTimeField(db_index=True, null=True, blank=True)

    def __str__(self):
        return self.title or self.url


class Priority(AuditMixin, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name or ""


class Label(AuditMixin, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name or ""


class Reminder(AuditMixin, TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    time = models.DurationField()

    def __str__(self):
        return str(self.time)


class Video(AuditMixin, HashMixin, TimeStampedModel):
    HASH_FIELDS = ["url"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    url = EncryptedTextField(unique=True, null=True, blank=True)
    url_hash = models.CharField(max_length=64, db_index=True, unique=True, null=True, blank=True)

    title = EncryptedCharField(max_length=255, null=True, blank=True)
    description = EncryptedTextField(null=True, blank=True)

    start_from = models.PositiveSmallIntegerField(default=0)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    priority = models.ForeignKey(Priority, null=True, blank=True, on_delete=models.SET_NULL)

    labels = models.ManyToManyField(Label, blank=True)
    channels = models.ManyToManyField(Channel, blank=True)

    checkout = models.DateTimeField(db_index=True, null=True, blank=True)
    deadline = models.DateTimeField(db_index=True, null=True, blank=True)
    reminders = models.ManyToManyField(Reminder, blank=True)

    STATUS_CHOICES = [
        ("new", "New"),
        ("watched", "Watched"),
        ("skipped", "Skipped"),
        ("archived", "Archived"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title or self.url

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "url_hash"], name="unique_user_video")
        ]


class Playlist(AuditMixin, HashMixin, TimeStampedModel):
    HASH_FIELDS = ["url"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    url = EncryptedTextField(unique=True, null=True, blank=True)
    url_hash = models.CharField(max_length=64, db_index=True, unique=True, null=True, blank=True)

    title = EncryptedCharField(max_length=255, null=True, blank=True)
    next_video = models.CharField(max_length=255, null=True, blank=True)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL)

    checkout = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title or self.url
