from django.contrib import admin
from django.utils.html import format_html

from .models import TaxInvoice, TaxInvoiceItem, TaxType


class TaxInvoiceItemInline(admin.TabularInline):
    model = TaxInvoiceItem
    extra = 0
    readonly_fields = ("total_amount",)
    fields = ("tax_type", "description", "quantity", "unit_amount", "total_amount")


@admin.register(TaxType)
class TaxTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "rate_type", "rate", "applicability", "is_mandatory", "is_active")
    list_filter = ("category", "rate_type", "applicability", "is_mandatory", "is_active")
    search_fields = ("name", "code")
    list_editable = ("is_active",)


@admin.register(TaxInvoice)
class TaxInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number", "booking_reference", "service_type",
        "passenger_name", "total_tax_amount", "status_badge", "is_paid", "created_at",
    )
    list_filter = ("service_type", "status", "is_paid")
    search_fields = ("invoice_number", "booking_reference", "passenger_name", "passenger_email")
    readonly_fields = ("invoice_number", "created_at", "updated_at")
    inlines = [TaxInvoiceItemInline]
    date_hierarchy = "created_at"

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "DRAFT": "#6b7280",
            "ISSUED": "#2563eb",
            "PAID": "#16a34a",
            "OVERDUE": "#dc2626",
            "CANCELLED": "#9ca3af",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display(),
        )
