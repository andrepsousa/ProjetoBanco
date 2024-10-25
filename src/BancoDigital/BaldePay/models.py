from django.db import models
from django.contrib.auth.hashers import make_password


class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    date_birth = models.DateField()
    phone = models.CharField(max_length=15)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
