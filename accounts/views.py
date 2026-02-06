"""
Account views for the Airport Management System.

User dashboard, profile management, and booking history.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from bookings.models import Booking

from .forms import ProfileForm, UserUpdateForm
from .models import Profile


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User dashboard with overview of bookings and account information.
    """

    template_name = "accounts/dashboard.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get recent bookings
        context["recent_bookings"] = Booking.objects.filter(
            user=user
        ).select_related(
            "flight", "flight__airline", "flight__origin", "flight__destination"
        ).order_by("-created_at")[:5]

        # Get upcoming flights
        context["upcoming_flights"] = Booking.objects.filter(
            user=user,
            flight__scheduled_departure__gt=timezone.now(),
            status__in=["CONFIRMED", "CHECKED_IN"]
        ).select_related(
            "flight", "flight__airline", "flight__origin", "flight__destination"
        ).order_by("flight__scheduled_departure")[:3]

        # Booking counts
        context["total_bookings"] = Booking.objects.filter(user=user).count()
        context["completed_bookings"] = Booking.objects.filter(
            user=user, status="COMPLETED"
        ).count()

        # Profile completion
        if hasattr(user, 'profile'):
            profile = user.profile
            filled_fields = 0
            total_fields = 10
            if profile.phone_number: filled_fields += 1
            if profile.date_of_birth: filled_fields += 1
            if profile.nationality: filled_fields += 1
            if profile.passport_number: filled_fields += 1
            if profile.passport_expiry: filled_fields += 1
            if profile.address_line1: filled_fields += 1
            if profile.city: filled_fields += 1
            if profile.emergency_contact_name: filled_fields += 1
            if profile.emergency_contact_phone: filled_fields += 1
            if profile.avatar: filled_fields += 1
            context["profile_completion"] = int((filled_fields / total_fields) * 100)
        else:
            context["profile_completion"] = 0

        # Loyalty info
        if hasattr(user, 'profile'):
            context["loyalty_points"] = user.profile.loyalty_points
            context["loyalty_tier"] = user.profile.loyalty_tier
        else:
            context["loyalty_points"] = 0
            context["loyalty_tier"] = "Bronze"

        return context


class BookingListView(LoginRequiredMixin, ListView):
    """
    List all user bookings with filtering options.
    """

    model = Booking
    template_name = "accounts/bookings_list.html"
    context_object_name = "bookings"
    paginate_by = 10
    login_url = "/accounts/login/"

    def get_queryset(self):
        queryset = Booking.objects.filter(
            user=self.request.user
        ).select_related(
            "flight", "flight__airline", "flight__origin", "flight__destination"
        ).order_by("-created_at")

        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        # Filter by time period
        period = self.request.GET.get("period")
        if period == "upcoming":
            queryset = queryset.filter(
                flight__scheduled_departure__gt=timezone.now()
            )
        elif period == "past":
            queryset = queryset.filter(
                flight__scheduled_departure__lte=timezone.now()
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["period_filter"] = self.request.GET.get("period", "")
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed view of a single booking.
    """

    model = Booking
    template_name = "accounts/booking_detail.html"
    context_object_name = "booking"
    login_url = "/accounts/login/"

    def get_object(self):
        return get_object_or_404(
            Booking.objects.select_related(
                "flight", "flight__airline", "flight__origin", "flight__destination",
                "flight__aircraft", "flight__departure_gate"
            ),
            reference=self.kwargs["reference"],
            user=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["passengers"] = self.object.passengers.all()
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View user profile.
    """

    template_name = "accounts/profile.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Ensure profile exists
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)

        context["profile"] = user.profile
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Edit user profile.
    """

    template_name = "accounts/profile_edit.html"
    login_url = "/accounts/login/"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
        return user.profile

    def get_form_class(self):
        return ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user form for name/email
        if self.request.POST:
            context["user_form"] = UserUpdateForm(
                self.request.POST,
                instance=self.request.user
            )
        else:
            context["user_form"] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        user_form = UserUpdateForm(self.request.POST, instance=self.request.user)
        if user_form.is_valid():
            user_form.save()
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)
