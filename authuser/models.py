from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group
from django.utils import timezone

student_group, created = Group.objects.get_or_create(name='Student')
contributor_group, created = Group.objects.get_or_create(name='Contributor')
volunteer_group, created = Group.objects.get_or_create(name='Volunteer')
admin_group, created = Group.objects.get_or_create(name='Admin')

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the provided email and password.
        """
        if not email:
            raise ValueError("The given email address must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model that uses email addresses instead of usernames, and
    name instead of first / last name fields.

    All other fields from the Django auth.User model are kept to
    ensure maximum compatibility with the built in management
    commands.
    """

    ROLE_CHOICES = (
        (1, "Student"),
        (2, "Contributor"),
        (3, "Volunteer"),
        (4, "Admin"),
    )

    email = models.EmailField(blank=True, default="", unique=True)
    name = models.CharField(max_length=200, blank=True, default="")
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=2, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_contributor = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)

    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name or self.email.split("@")[0]
