from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from django.conf import settings


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class UserManager(BaseUserManager):
    def create_user(self, email,username, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        username = username
        user = self.model(email=email,username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username,  password, **extra_fields)

class User(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

#class RefreshToken(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    token = models.UUIDField(default=uuid.uuid4, unique=True)
#    expires_at = models.DateTimeField()
#
#    def __str__(self):
#        return f"Token for {self.user.username}"

class Price(models.Model):
    symbol = models.CharField(max_length=60)
    currency = models.CharField(max_length=60)
    value = models.DecimalField(max_digits=18, decimal_places=8)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.symbol} - {self.currency} : {self.value} at {self.date}"
    

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallets")
    address = models.CharField(max_length=42, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address