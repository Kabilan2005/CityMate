# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string

class User(AbstractUser):
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    preferred_city = models.CharField(max_length=100, blank=True, default="Coimbatore")
    AREA_CHOICES = [
        ('rs_puram', 'RS Puram'),
        ('gandhipuram', 'Gandhipuram'),
        ('peelamedu', 'Peelamedu'),
        ('hopes', 'Hope College'),
        ('saibaba_colony', 'Saibaba Colony'),
        ('singanallur', 'Singanallur'),
        ('other', 'Other/Not Listed'),
    ]
    preferred_area = models.CharField(
        max_length=100,
        choices=AREA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Preferred Area" 
    )
    preferred_price = models.CharField(
        max_length=10,
        choices=[
            ('economical', 'Budget Friendly'),
            ('average', 'Affordable'),
            ('premium', 'Costly')
        ],
        blank=True,
        null=True
    )
    taste_tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated tags, e.g., vegetarian, chettinad"
    )
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Override group relationships to avoid clash with AbstractUser
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_users',
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_users_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username


class OTP(models.Model):
    PURPOSE_CHOICES = [
        ('signup', 'Account Signup'),
        ('reset', 'Password Reset'),
        ('profile_update', 'Profile Update'), 
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    contact_info = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    type = models.CharField(max_length=10, choices=[('email', 'Email'), ('phone', 'Phone')])

    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='signup')
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at 