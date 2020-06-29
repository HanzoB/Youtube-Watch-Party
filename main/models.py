from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


# Create your models here.
class Gen_room(models.Model):
    random_url = models.UUIDField(default=uuid.uuid4)
    time_created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
