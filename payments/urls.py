"""
URL configuration for payments app.

Payment processing and Paystack integration endpoints.
"""

from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    # Payment initiation
    path("initiate/<str:reference>/", views.InitiatePaymentView.as_view(), name="initiate"),

    # Payment verification (Paystack callback)
    path("verify/<str:reference>/", views.VerifyPaymentView.as_view(), name="verify"),

    # Payment result pages
    path("success/<str:reference>/", views.PaymentSuccessView.as_view(), name="success"),
    path("failed/<str:reference>/", views.PaymentFailedView.as_view(), name="failed"),

    # Payment history
    path("history/", views.PaymentHistoryView.as_view(), name="history"),
    path("detail/<uuid:pk>/", views.PaymentDetailView.as_view(), name="detail"),

    # Retry payment
    path("retry/<str:reference>/", views.RetryPaymentView.as_view(), name="retry"),

    # AJAX status check
    path("status/<str:reference>/", views.CheckPaymentStatusView.as_view(), name="status"),

    # Paystack webhook
    path("webhook/paystack/", views.PaystackWebhookView.as_view(), name="paystack_webhook"),
]
