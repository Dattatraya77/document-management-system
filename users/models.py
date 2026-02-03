from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import pytz


# ======================================================
# Timezone Choices (Dynamic & Standard)
# ======================================================

TZ_CHOICES = [(tz, tz) for tz in pytz.all_timezones]


# ======================================================
# User Profile Model
# ======================================================

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    image = models.ImageField(
        upload_to="profile_pics/",
        default="default.jpg",
        blank=True
    )

    client_tz = models.CharField(
        max_length=100,
        choices=TZ_CHOICES,
        default="Asia/Kolkata"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Safely resize image (works with local & cloud storage)
        try:
            if self.image:
                img = Image.open(self.image)

                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300))
                    img.save(self.image.path)
        except Exception:
            # Prevent save crashes due to image/storage issues
            pass

