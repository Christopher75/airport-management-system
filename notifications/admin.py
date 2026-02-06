"""
Admin configuration for the notifications app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""

    list_display = (
        "id_short",
        "user",
        "notification_type",
        "title_preview",
        "channel",
        "priority_badge",
        "is_read",
        "is_sent",
        "created_at",
    )
    list_filter = (
        "notification_type",
        "channel",
        "priority",
        "is_read",
        "is_sent",
        "is_delivered",
        "created_at",
    )
    search_fields = (
        "user__email",
        "title",
        "message",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("user",)

    fieldsets = (
        (
            _("Recipient"),
            {
                "fields": ("user",)
            },
        ),
        (
            _("Content"),
            {
                "fields": (
                    "notification_type",
                    "title",
                    "message",
                    "html_message",
                )
            },
        ),
        (
            _("Delivery"),
            {
                "fields": (
                    ("channel", "priority"),
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    ("is_read", "read_at"),
                    ("is_sent", "sent_at"),
                    ("is_delivered", "delivered_at"),
                )
            },
        ),
        (
            _("Related Objects"),
            {
                "fields": (
                    "related_booking_id",
                    "related_flight_id",
                    "related_payment_id",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Action"),
            {
                "fields": (
                    "action_url",
                    "action_text",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Error"),
            {
                "fields": ("error_message",),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("read_at", "sent_at", "delivered_at")

    actions = ["mark_as_read", "mark_as_sent"]

    def id_short(self, obj):
        """Display shortened UUID."""
        return str(obj.id)[:8]

    id_short.short_description = _("ID")

    def title_preview(self, obj):
        """Display truncated title."""
        if len(obj.title) > 40:
            return f"{obj.title[:40]}..."
        return obj.title

    title_preview.short_description = _("Title")

    def priority_badge(self, obj):
        """Display priority as a colored badge."""
        colors = {
            "LOW": "#6c757d",
            "NORMAL": "#007bff",
            "HIGH": "#ffc107",
            "URGENT": "#dc3545",
        }
        color = colors.get(obj.priority, "#6c757d")
        text_color = "black" if obj.priority == "HIGH" else "white"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 2px 6px; '
            'border-radius: 3px; font-size: 10px;">{}</span>',
            color,
            text_color,
            obj.get_priority_display(),
        )

    priority_badge.short_description = _("Priority")
    priority_badge.admin_order_field = "priority"

    @admin.action(description=_("Mark selected as read"))
    def mark_as_read(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
        self.message_user(request, f"{updated} notification(s) marked as read.")

    @admin.action(description=_("Mark selected as sent"))
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(is_sent=False).update(
            is_sent=True,
            sent_at=timezone.now(),
        )
        self.message_user(request, f"{updated} notification(s) marked as sent.")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationPreference model."""

    list_display = (
        "user",
        "email_booking",
        "email_flight_updates",
        "sms_flight_updates",
        "push_flight_updates",
        "quiet_hours_enabled",
    )
    list_filter = (
        "email_booking",
        "email_flight_updates",
        "sms_flight_updates",
        "push_flight_updates",
        "quiet_hours_enabled",
    )
    search_fields = ("user__email", "user__first_name", "user__last_name")
    raw_id_fields = ("user",)

    fieldsets = (
        (
            _("User"),
            {"fields": ("user",)},
        ),
        (
            _("Email Preferences"),
            {
                "fields": (
                    "email_booking",
                    "email_flight_updates",
                    "email_payment",
                    "email_promotions",
                    "email_account",
                )
            },
        ),
        (
            _("SMS Preferences"),
            {
                "fields": (
                    "sms_booking",
                    "sms_flight_updates",
                    "sms_payment",
                    "sms_promotions",
                )
            },
        ),
        (
            _("Push Notification Preferences"),
            {
                "fields": (
                    "push_booking",
                    "push_flight_updates",
                    "push_payment",
                    "push_promotions",
                )
            },
        ),
        (
            _("In-App Preferences"),
            {"fields": ("in_app_all",)},
        ),
        (
            _("Quiet Hours"),
            {
                "fields": (
                    "quiet_hours_enabled",
                    ("quiet_hours_start", "quiet_hours_end"),
                )
            },
        ),
    )
