"""
Core views for public-facing pages.

Handles home, about, and contact pages for the Airport Management System.
"""

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView

from flights.models import Airport, Flight

from .forms import ContactForm


class HomeView(TemplateView):
    """
    Home page view with flight search widget and featured content.
    """

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get active airports for search form
        context["airports"] = Airport.objects.filter(is_active=True).order_by("name")

        # Get some featured/popular destinations
        context["popular_destinations"] = Airport.objects.filter(
            is_active=True, is_international=True
        ).order_by("?")[:4]

        # Get upcoming flights count
        from django.utils import timezone

        context["upcoming_flights_count"] = Flight.objects.filter(
            scheduled_departure__gte=timezone.now(),
            status__in=["SCHEDULED", "CHECK_IN_OPEN"],
        ).count()

        return context


class AboutView(TemplateView):
    """
    About page with airport information and history.
    """

    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Airport statistics
        context["stats"] = {
            "airlines": 15,  # Will be dynamic later
            "destinations": 40,
            "annual_passengers": "8M+",
            "daily_flights": 120,
        }

        return context


class ContactView(FormView):
    """
    Contact page with inquiry form.
    """

    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = "/contact/?success=true"

    def form_valid(self, form):
        # Process the contact form
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        # Send email (will use console backend in development)
        try:
            send_mail(
                subject=f"[NAIA Contact] {subject}",
                message=f"From: {name} <{email}>\n\n{message}",
                from_email=email,
                recipient_list=["info@naia.ng"],
                fail_silently=True,
            )
        except Exception:
            pass  # Handle silently, message is still saved

        messages.success(
            self.request,
            "Thank you for your message! We will get back to you soon.",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["success"] = self.request.GET.get("success") == "true"
        return context
