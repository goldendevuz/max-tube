from django.db import models
from django_extensions.db.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name or ""


class Channel(TimeStampedModel):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=4000, null=True, blank=True)
    total_watch = models.PositiveSmallIntegerField(default=0)
    next_video = models.CharField(max_length=255, null=True, blank=True)
    has_new_video = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="channels"
    )

    checkout = models.DateTimeField(db_index=True, null=True, blank=True)

    def __str__(self):
        return self.title or self.url


class Video(TimeStampedModel):
    url = models.URLField(unique=True)
    start_from = models.PositiveSmallIntegerField(default=0)

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="videos"
    )

    # 🔥 Many-to-Many (asosiy o‘zgarish)
    channels = models.ManyToManyField(
        Channel,
        blank=True,
        related_name="videos"
    )

    checkout = models.DateTimeField(db_index=True)

    def __str__(self):
        return self.url or ""


class Playlist(TimeStampedModel):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    next_video = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL)
    checkout = models.DateTimeField()

    def __str__(self):
        return self.url or ""
