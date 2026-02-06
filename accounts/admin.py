"""
Admin configuration for the accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    """Inline admin for Profile to show within User admin."""

    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"

    fieldsets = (
        (
            _("Personal Information"),
            {
                "fields": (
                    ("title", "gender"),
                    "date_of_birth",
                    "phone_number",
                    "nationality",
                    "avatar",
                )
            },
        ),
        (
            _("Travel Documents"),
            {
                "fields": (
                    "passport_number",
                    "passport_expiry",
                    "passport_country",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    ("city", "state"),
                    ("postal_code", "country"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Loyalty Program"),
            {
                "fields": (
                    "loyalty_number",
                    ("loyalty_points", "loyalty_tier"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Emergency Contact"),
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Preferences"),
            {
                "fields": (
                    ("preferred_seat", "meal_preference"),
                    "special_assistance",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model."""

    inlines = [ProfileInline]

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # Define fieldsets for add/change forms
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name")},
        ),
        (
            _("Role & Permissions"),
            {
                "fields": (
                    "role",
                    "airline",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")

    def get_inline_instances(self, request, obj=None):
        """Only show profile inline for existing users."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Standalone admin for Profile model."""

    list_display = (
        "user",
        "phone_number",
        "nationality",
        "loyalty_tier",
        "loyalty_points",
    )
    list_filter = ("loyalty_tier", "nationality", "gender")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone_number",
        "passport_number",
    )
    raw_id_fields = ("user",)

    fieldsets = (
        (
            _("User"),
            {"fields": ("user",)},
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    ("title", "gender"),
                    "date_of_birth",
                    "phone_number",
                    "nationality",
                    "avatar",
                )
            },
        ),
        (
            _("Travel Documents"),
            {
                "fields": (
                    "passport_number",
                    "passport_expiry",
                    "passport_country",
                )
            },
        ),
        (
            _("Address"),
            {
                "fields": (
                    "address_line1",
                    "address_line2",
                    ("city", "state"),
                    ("postal_code", "country"),
                )
            },
        ),
        (
            _("Loyalty Program"),
            {
                "fields": (
                    "loyalty_number",
                    ("loyalty_points", "loyalty_tier"),
                )
            },
        ),
        (
            _("Emergency Contact"),
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                    "emergency_contact_relationship",
                )
            },
        ),
        (
            _("Preferences"),
            {
                "fields": (
                    ("preferred_seat", "meal_preference"),
                    "special_assistance",
                )
            },
        ),
    )
