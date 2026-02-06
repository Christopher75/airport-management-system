"""
Notification views for the Airport Management System.

In-app notification listing, marking as read, and preferences.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from .models import Notification, NotificationChannel, NotificationPreference
from .services import notification_service


class NotificationListView(LoginRequiredMixin, ListView):
    """
    List all in-app notifications for the user.
    """

    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 20
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            channel=NotificationChannel.IN_APP,
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_count"] = notification_service.get_unread_count(self.request.user)
        return context


class MarkNotificationReadView(LoginRequiredMixin, View):
    """
    Mark a single notification as read.
    """

    login_url = "/accounts/login/"

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user,
        )
        notification.mark_as_read()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        # Redirect to action URL if available
        if notification.action_url:
            return redirect(notification.action_url)

        return redirect("notifications:list")


class MarkAllReadView(LoginRequiredMixin, View):
    """
    Mark all notifications as read.
    """

    login_url = "/accounts/login/"

    def post(self, request):
        count = notification_service.mark_all_as_read(request.user)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "count": count})

        return redirect("notifications:list")


class NotificationPreferencesView(LoginRequiredMixin, UpdateView):
    """
    Update notification preferences.
    """

    template_name = "notifications/preferences.html"
    model = NotificationPreference
    fields = [
        "email_booking",
        "email_flight_updates",
        "email_payment",
        "email_promotions",
        "email_account",
        "sms_booking",
        "sms_flight_updates",
        "sms_payment",
        "sms_promotions",
        "push_booking",
        "push_flight_updates",
        "push_payment",
        "push_promotions",
        "in_app_all",
        "quiet_hours_enabled",
        "quiet_hours_start",
        "quiet_hours_end",
    ]
    success_url = reverse_lazy("notifications:preferences")
    login_url = "/accounts/login/"

    def get_object(self):
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj


class UnreadCountView(LoginRequiredMixin, View):
    """
    API endpoint to get unread notification count.
    """

    login_url = "/accounts/login/"

    def get(self, request):
        count = notification_service.get_unread_count(request.user)
        return JsonResponse({"count": count})


class RecentNotificationsView(LoginRequiredMixin, View):
    """
    API endpoint to get recent notifications.
    """

    login_url = "/accounts/login/"

    def get(self, request):
        notifications = notification_service.get_recent_notifications(
            request.user,
            limit=5,
        )

        data = [
            {
                "id": str(n.id),
                "type": n.notification_type,
                "title": n.title,
                "message": n.message[:100] + "..." if len(n.message) > 100 else n.message,
                "is_read": n.is_read,
                "action_url": n.action_url,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]

        return JsonResponse({
            "notifications": data,
            "unread_count": notification_service.get_unread_count(request.user),
        })
