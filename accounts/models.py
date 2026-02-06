"""
User and Profile models for the Airport Management System.

Implements a custom user model with email authentication and role-based access control.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel
from core.validators import validate_passport_number, validate_phone_number

from .managers import CustomUserManager


class UserRole(models.TextChoices):
    """User role choices for role-based access control."""

    PASSENGER = "PASSENGER", _("Passenger")
    AIRLINE_STAFF = "AIRLINE_STAFF", _("Airline Staff")
    AIRPORT_STAFF = "AIRPORT_STAFF", _("Airport Staff")
    ADMIN = "ADMIN", _("Administrator")


class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model using email for authentication.

    This model replaces Django's default User model to support:
    - Email-based authentication (no username)
    - Role-based access control
    - Extended user information
    """

    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_("Required. A valid email address."),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PASSENGER,
        help_text=_("User's role in the system"),
    )

    # Status fields
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    # For airline staff - link to their airline
    airline = models.ForeignKey(
        "airlines.Airline",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_members",
        help_text=_("Airline this staff member belongs to (for airline staff only)"),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    @property
    def is_passenger(self):
        return self.role == UserRole.PASSENGER

    @property
    def is_airline_staff(self):
        return self.role == UserRole.AIRLINE_STAFF

    @property
    def is_airport_staff(self):
        return self.role == UserRole.AIRPORT_STAFF

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN


class Profile(TimeStampedModel):
    """
    Extended user profile for passengers.

    Stores additional information like travel documents, preferences,
    loyalty program data, and emergency contacts.
    """

    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        OTHER = "O", _("Other")
        PREFER_NOT_TO_SAY = "N", _("Prefer not to say")

    class Title(models.TextChoices):
        MR = "MR", _("Mr.")
        MRS = "MRS", _("Mrs.")
        MS = "MS", _("Ms.")
        DR = "DR", _("Dr.")
        PROF = "PROF", _("Prof.")

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Personal Information
    title = models.CharField(
        _("title"),
        max_length=10,
        choices=Title.choices,
        blank=True,
    )
    gender = models.CharField(
        _("gender"),
        max_length=1,
        choices=Gender.choices,
        blank=True,
    )
    date_of_birth = models.DateField(
        _("date of birth"),
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
    )
    nationality = models.CharField(
        _("nationality"),
        max_length=100,
        default="Nigerian",
        blank=True,
    )

    # Travel Documents
    passport_number = models.CharField(
        _("passport number"),
        max_length=20,
        blank=True,
        validators=[validate_passport_number],
    )
    passport_expiry = models.DateField(
        _("passport expiry date"),
        null=True,
        blank=True,
    )
    passport_country = models.CharField(
        _("passport issuing country"),
        max_length=100,
        default="Nigeria",
        blank=True,
    )

    # Address
    address_line1 = models.CharField(
        _("address line 1"),
        max_length=255,
        blank=True,
    )
    address_line2 = models.CharField(
        _("address line 2"),
        max_length=255,
        blank=True,
    )
    city = models.CharField(
        _("city"),
        max_length=100,
        blank=True,
    )
    state = models.CharField(
        _("state/province"),
        max_length=100,
        blank=True,
    )
    postal_code = models.CharField(
        _("postal code"),
        max_length=20,
        blank=True,
    )
    country = models.CharField(
        _("country"),
        max_length=100,
        default="Nigeria",
        blank=True,
    )

    # Loyalty Program
    loyalty_number = models.CharField(
        _("loyalty number"),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Frequent flyer loyalty program number"),
    )
    loyalty_points = models.PositiveIntegerField(
        _("loyalty points"),
        default=0,
    )
    loyalty_tier = models.CharField(
        _("loyalty tier"),
        max_length=20,
        default="Bronze",
        choices=[
            ("Bronze", "Bronze"),
            ("Silver", "Silver"),
            ("Gold", "Gold"),
            ("Platinum", "Platinum"),
        ],
    )

    # Emergency Contact
    emergency_contact_name = models.CharField(
        _("emergency contact name"),
        max_length=255,
        blank=True,
    )
    emergency_contact_phone = models.CharField(
        _("emergency contact phone"),
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
    )
    emergency_contact_relationship = models.CharField(
        _("relationship"),
        max_length=50,
        blank=True,
    )

    # Preferences
    preferred_seat = models.CharField(
        _("preferred seat"),
        max_length=20,
        choices=[
            ("WINDOW", "Window"),
            ("AISLE", "Aisle"),
            ("MIDDLE", "Middle"),
            ("NO_PREFERENCE", "No Preference"),
        ],
        default="NO_PREFERENCE",
    )
    meal_preference = models.CharField(
        _("meal preference"),
        max_length=50,
        choices=[
            ("REGULAR", "Regular"),
            ("VEGETARIAN", "Vegetarian"),
            ("VEGAN", "Vegan"),
            ("HALAL", "Halal"),
            ("KOSHER", "Kosher"),
            ("GLUTEN_FREE", "Gluten Free"),
            ("NO_PREFERENCE", "No Preference"),
        ],
        default="NO_PREFERENCE",
    )
    special_assistance = models.TextField(
        _("special assistance requirements"),
        blank=True,
        help_text=_("Any special assistance or accessibility needs"),
    )

    # Profile Picture
    avatar = models.ImageField(
        _("profile picture"),
        upload_to="avatars/",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return f"Profile of {self.user.email}"

    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country,
        ]
        return ", ".join(part for part in parts if part)
