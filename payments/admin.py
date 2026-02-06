"""
Admin configuration for the payments app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Payment, PaymentLog, PaymentStatus


class PaymentLogInline(admin.TabularInline):
    """Inline admin for PaymentLog within Payment admin."""

    model = PaymentLog
    extra = 0
    readonly_fields = ("event_type", "message", "created_at", "ip_address")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""

    inlines = [PaymentLogInline]

    list_display = (
        "id_short",
        "booking",
        "user",
        "formatted_amount",
        "payment_method",
        "status_badge",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "payment_method", "currency", "created_at")
    search_fields = (
        "booking__reference",
        "user__email",
        "paystack_reference",
        "card_last4",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("booking", "user")

    fieldsets = (
        (
            _("Booking Information"),
            {
                "fields": (
                    ("booking", "user"),
                )
            },
        ),
        (
            _("Payment Details"),
            {
                "fields": (
                    ("amount", "currency"),
                    ("payment_method", "status"),
                )
            },
        ),
        (
            _("Paystack References"),
            {
                "fields": (
                    "paystack_reference",
                    "paystack_access_code",
                    "paystack_authorization_url",
                )
            },
        ),
        (
            _("Card/Bank Details"),
            {
                "fields": (
                    ("card_last4", "card_type"),
                    ("bank_name", "channel"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Response"),
            {
                "fields": (
                    "gateway_response",
                    "ip_address",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "paid_at",
                )
            },
        ),
        (
            _("Refund"),
            {
                "fields": (
                    ("refund_amount", "refunded_at"),
                    "refund_reason",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("metadata",),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = (
        "paystack_reference",
        "paystack_access_code",
        "paystack_authorization_url",
        "card_last4",
        "card_type",
        "bank_name",
        "channel",
        "gateway_response",
        "ip_address",
        "paid_at",
        "metadata",
    )

    def id_short(self, obj):
        """Display shortened UUID."""
        return str(obj.id)[:8]

    id_short.short_description = _("ID")

    def formatted_amount(self, obj):
        """Display amount formatted as currency."""
        return f"₦{obj.amount:,.2f}"

    formatted_amount.short_description = _("Amount")
    formatted_amount.admin_order_field = "amount"

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "PENDING": "#ffc107",
            "PROCESSING": "#17a2b8",
            "COMPLETED": "#28a745",
            "FAILED": "#dc3545",
            "CANCELLED": "#6c757d",
            "REFUNDED": "#fd7e14",
            "PARTIALLY_REFUNDED": "#e83e8c",
        }
        color = colors.get(obj.status, "#6c757d")
        text_color = "black" if obj.status in ["PENDING", "PROCESSING"] else "white"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            text_color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")
    status_badge.admin_order_field = "status"


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentLog model."""

    list_display = (
        "payment_short",
        "event_type",
        "message_preview",
        "ip_address",
        "created_at",
    )
    list_filter = ("event_type", "created_at")
    search_fields = ("payment__paystack_reference", "message")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("payment",)

    readonly_fields = (
        "payment",
        "event_type",
        "message",
        "data",
        "ip_address",
        "created_at",
    )

    def payment_short(self, obj):
        """Display shortened payment ID."""
        return str(obj.payment.id)[:8]

    payment_short.short_description = _("Payment")

    def message_preview(self, obj):
        """Display truncated message."""
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message

    message_preview.short_description = _("Message")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
