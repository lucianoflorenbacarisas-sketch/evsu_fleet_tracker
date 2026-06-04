from django.db import models
from accounts.models import User


class ActivityLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    action = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.user.username} - {self.action}"