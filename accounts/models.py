from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    town = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    