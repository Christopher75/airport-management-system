"""
View tests for the NAIA Airport Management System.

Tests for Django views including public pages, authentication, booking flow, and dashboard.
"""

import pytest
from django.urls import reverse
from django.test import Client


# ============================================================================
# Public Page Tests
# ============================================================================

@pytest.mark.django_db
class TestPublicPages:
    """Tests for public pages."""

    def test_home_page(self, client):
        """Test home page loads successfully."""
        url = reverse('core:home')
        response = client.get(url)
        assert response.status_code == 200
        assert 'NAIA' in response.content.decode() or 'Airport' in response.content.decode()

    def test_about_page(self, client):
        """Test about page loads successfully."""
        url = reverse('core:about')
        response = client.get(url)
        assert response.status_code == 200

    def test_contact_page(self, client):
        """Test contact page loads successfully."""
        url = reverse('core:contact')
        response = client.get(url)
        assert response.status_code == 200

    def test_contact_form_submission(self, client):
        """Test contact form submission."""
        url = reverse('core:contact')
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        }
        response = client.post(url, data)
        # Should redirect after successful submission
        assert response.status_code in [200, 302]


# ============================================================================
# Authentication View Tests
# ============================================================================

@pytest.mark.django_db
class TestAuthenticationViews:
    """Tests for authentication views."""

    def test_login_page_loads(self, client):
        """Test login page loads."""
        url = reverse('account_login')
        response = client.get(url)
        assert response.status_code == 200

    def test_signup_page_loads(self, client):
        """Test signup page loads."""
        url = reverse('account_signup')
        response = client.get(url)
        assert response.status_code == 200

    def test_login_success(self, client, user, user_password):
        """Test successful login."""
        url = reverse('account_login')
        data = {
            'login': user.email,
            'password': user_password
        }
        response = client.post(url, data)
        # Should redirect after successful login
        assert response.status_code == 302

    def test_login_failure(self, client, user):
        """Test login with wrong password."""
        url = reverse('account_login')
        data = {
            'login': user.email,
            'password': 'WrongPassword123!'
        }
        response = client.post(url, data)
        # Should stay on page with error
        assert response.status_code == 200

    def test_logout(self, authenticated_client):
        """Test logout."""
        url = reverse('account_logout')
        response = authenticated_client.post(url)
        # Should redirect after logout
        assert response.status_code == 302

    def test_password_reset_page(self, client):
        """Test password reset page loads."""
        url = reverse('account_reset_password')
        response = client.get(url)
        assert response.status_code == 200


# ============================================================================
# Flight Search View Tests
# ============================================================================

@pytest.mark.django_db
class TestFlightSearchViews:
    """Tests for flight search views."""

    def test_flight_search_page(self, client, airport_abuja, airport_lagos):
        """Test flight search page loads."""
        url = reverse('flights:search')
        response = client.get(url)
        assert response.status_code == 200

    def test_flight_search_with_params(self, client, flight, airport_abuja, airport_lagos):
        """Test flight search with parameters."""
        url = reverse('flights:search')
        params = {
            'origin': airport_abuja.pk,
            'destination': airport_lagos.pk,
            'departure_date': flight.scheduled_departure.date().isoformat(),
            'passengers': 1
        }
        response = client.get(url, params)
        assert response.status_code == 200

    def test_flight_list_page(self, client, flight):
        """Test flight list page."""
        url = reverse('flights:list')
        response = client.get(url)
        assert response.status_code == 200

    def test_flight_detail_page(self, client, flight):
        """Test flight detail page."""
        url = reverse('flights:detail', kwargs={'pk': flight.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_flight_status_board(self, client, flight):
        """Test flight status board page."""
        url = reverse('flights:status_board')
        response = client.get(url)
        assert response.status_code == 200


# ============================================================================
# Booking Flow View Tests
# ============================================================================

@pytest.mark.django_db
class TestBookingFlowViews:
    """Tests for booking flow views."""

    def test_select_flight_page(self, authenticated_client, flight):
        """Test select flight page loads."""
        url = reverse('bookings:select_flight', kwargs={'pk': flight.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_select_flight_requires_login(self, client, flight):
        """Test that select flight page requires login."""
        url = reverse('bookings:select_flight', kwargs={'pk': flight.pk})
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response.url.lower() or 'accounts' in response.url.lower()

    def test_passenger_form_page(self, authenticated_client, flight):
        """Test passenger form page."""
        # First, select a flight
        session = authenticated_client.session
        session['booking'] = {
            'flight_id': flight.pk,
            'seat_class': 'ECONOMY',
            'passengers': 1
        }
        session.save()

        url = reverse('bookings:passengers')
        response = authenticated_client.get(url)
        # May redirect if no booking in session
        assert response.status_code in [200, 302]

    def test_booking_review_page(self, authenticated_client, flight):
        """Test booking review page."""
        url = reverse('bookings:review')
        response = authenticated_client.get(url)
        # May redirect if no booking in session
        assert response.status_code in [200, 302]


# ============================================================================
# Dashboard View Tests
# ============================================================================

@pytest.mark.django_db
class TestDashboardViews:
    """Tests for user dashboard views."""

    def test_dashboard_requires_login(self, client):
        """Test dashboard requires login."""
        url = reverse('accounts:dashboard')
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302

    def test_dashboard_loads_for_authenticated_user(self, authenticated_client):
        """Test dashboard loads for authenticated user."""
        url = reverse('accounts:dashboard')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_profile_page(self, authenticated_client):
        """Test profile page loads."""
        url = reverse('accounts:profile')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_profile_edit_page(self, authenticated_client):
        """Test profile edit page loads."""
        url = reverse('accounts:profile_edit')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_profile_update(self, authenticated_client, user):
        """Test profile update."""
        url = reverse('accounts:profile_edit')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+2348012345678'
        }
        response = authenticated_client.post(url, data)
        # Should redirect after successful update
        assert response.status_code in [200, 302]

    def test_bookings_list_page(self, authenticated_client, booking):
        """Test bookings list page."""
        url = reverse('accounts:bookings')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_booking_detail_page(self, authenticated_client, booking):
        """Test booking detail page."""
        url = reverse('accounts:booking_detail', kwargs={'reference': booking.reference})
        response = authenticated_client.get(url)
        assert response.status_code == 200


# ============================================================================
# Analytics View Tests (Staff Only)
# ============================================================================

@pytest.mark.django_db
class TestAnalyticsViews:
    """Tests for analytics views (staff only)."""

    def test_analytics_requires_staff(self, authenticated_client):
        """Test analytics dashboard requires staff access."""
        url = reverse('analytics:dashboard')
        response = authenticated_client.get(url)
        # Regular user should be redirected or denied
        assert response.status_code in [302, 403]

    def test_analytics_loads_for_staff(self, staff_client):
        """Test analytics dashboard loads for staff."""
        url = reverse('analytics:dashboard')
        response = staff_client.get(url)
        assert response.status_code == 200

    def test_revenue_report_for_staff(self, staff_client):
        """Test revenue report loads for staff."""
        url = reverse('analytics:revenue_report')
        response = staff_client.get(url)
        assert response.status_code == 200

    def test_booking_report_for_staff(self, staff_client):
        """Test booking report loads for staff."""
        url = reverse('analytics:booking_report')
        response = staff_client.get(url)
        assert response.status_code == 200

    def test_flight_report_for_staff(self, staff_client):
        """Test flight report loads for staff."""
        url = reverse('analytics:flight_report')
        response = staff_client.get(url)
        assert response.status_code == 200


# ============================================================================
# E-Ticket View Tests
# ============================================================================

@pytest.mark.django_db
class TestETicketViews:
    """Tests for e-ticket views."""

    def test_eticket_requires_login(self, client, booking):
        """Test e-ticket download requires login."""
        url = reverse('bookings:eticket', kwargs={'reference': booking.reference})
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302

    def test_eticket_download(self, authenticated_client, booking, passenger, payment):
        """Test e-ticket download for confirmed booking."""
        url = reverse('bookings:eticket', kwargs={'reference': booking.reference})
        response = authenticated_client.get(url)
        # Should return PDF or redirect
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            assert response['Content-Type'] == 'application/pdf'


# ============================================================================
# Error Page Tests
# ============================================================================

@pytest.mark.django_db
class TestErrorPages:
    """Tests for error pages."""

    def test_404_page(self, client):
        """Test 404 page."""
        response = client.get('/nonexistent-page/')
        assert response.status_code == 404

    def test_flight_not_found(self, client):
        """Test accessing non-existent flight."""
        url = reverse('flights:detail', kwargs={'pk': 99999})
        response = client.get(url)
        assert response.status_code == 404
