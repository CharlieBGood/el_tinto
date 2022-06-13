from django.db import models
from django.contrib.auth.models import UserManager as BaseUserManager
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """ User Manager that knows how to create users via email instead of username """
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    
    objects = UserManager()
    
    email = models.EmailField(
        'email address',
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )
    
    phone_number = PhoneNumberField(blank=True)
    first_name = models.CharField(max_length=25, blank=True, default='')
    last_name = models.CharField(max_length=25, blank=True, default='')
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


#@receiver(post_save, sender=settings.AUTH_USER_MODEL)
#def create_auth_token(sender, instance=None, created=False, **kwargs):
#    if created:
#        Token.objects.create(user=instance)


class Unsuscribe(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    boring = models.BooleanField(default=False)
    invasive = models.BooleanField(default=False)
    variety = models.BooleanField(default=False)
    not_used = models.BooleanField(default=False)
    other_email = models.BooleanField(default=False)
    recomendation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user}'
