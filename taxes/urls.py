from django.urls import path

from . import views

app_name = "taxes"

urlpatterns = [
    path("", views.tax_home, name="home"),
    path("rates/", views.tax_rates_public, name="rates"),
    path("my-invoices/", views.my_tax_invoices, name="my_invoices"),
    path("invoice/<str:invoice_number>/", views.tax_invoice_detail, name="invoice_detail"),
    path("invoice/<str:invoice_number>/pay/", views.mark_invoice_paid, name="mark_paid"),
]
