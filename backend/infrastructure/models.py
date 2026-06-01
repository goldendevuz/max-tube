from django.db import models


class UserModel(models.Model):
    """Django ORM representation of the User aggregate root."""

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "auth_user"
        verbose_name = "user"
        verbose_name_plural = "users"


class VideoModel(models.Model):
    """Django ORM representation of the Video aggregate root."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="videos")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "video"
        verbose_name = "video"
        verbose_name_plural = "videos"
