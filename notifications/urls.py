"""
URL configuration for notifications app.
"""

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    # Notification list
    path("", views.NotificationListView.as_view(), name="list"),

    # Mark as read
    path("<uuid:pk>/read/", views.MarkNotificationReadView.as_view(), name="mark_read"),
    path("mark-all-read/", views.MarkAllReadView.as_view(), name="mark_all_read"),

    # Preferences
    path("preferences/", views.NotificationPreferencesView.as_view(), name="preferences"),

    # API endpoints
    path("api/unread-count/", views.UnreadCountView.as_view(), name="unread_count"),
    path("api/recent/", views.RecentNotificationsView.as_view(), name="recent"),
]
