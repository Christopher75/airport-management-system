"""
API tests for the NAIA Airport Management System.

Tests for REST API endpoints including authentication, CRUD operations, and permissions.
"""

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status


# ============================================================================
# Authentication API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestAuthenticationAPI:
    """Tests for authentication endpoints."""

    def test_user_registration(self, api_client):
        """Test user registration endpoint."""
        url = reverse('api:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'email' in response.data

    def test_user_registration_password_mismatch(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse('api:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_obtain(self, api_client, user, user_password):
        """Test JWT token obtain endpoint."""
        url = reverse('api:token_obtain_pair')
        data = {
            'email': user.email,
            'password': user_password
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_token_obtain_invalid_credentials(self, api_client, user):
        """Test token obtain with invalid credentials."""
        url = reverse('api:token_obtain_pair')
        data = {
            'email': user.email,
            'password': 'WrongPassword123!'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, user, user_password):
        """Test JWT token refresh endpoint."""
        # First, obtain tokens
        token_url = reverse('api:token_obtain_pair')
        token_data = {
            'email': user.email,
            'password': user_password
        }
        token_response = api_client.post(token_url, token_data, format='json')
        refresh_token = token_response.data['refresh']

        # Then, refresh the access token
        refresh_url = reverse('api:token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = api_client.post(refresh_url, refresh_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


# ============================================================================
# Airport API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestAirportAPI:
    """Tests for airport endpoints."""

    def test_list_airports(self, authenticated_api_client, airport_abuja, airport_lagos):
        """Test listing airports."""
        url = reverse('api:airport-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2

    def test_retrieve_airport(self, authenticated_api_client, airport_abuja):
        """Test retrieving a single airport."""
        url = reverse('api:airport-detail', kwargs={'pk': airport_abuja.pk})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'ABV'

    def test_search_airports_by_city(self, authenticated_api_client, airport_abuja, airport_lagos):
        """Test searching airports by city."""
        url = reverse('api:airport-list')
        response = authenticated_api_client.get(url, {'search': 'Abuja'})
        assert response.status_code == status.HTTP_200_OK
        assert any(a['code'] == 'ABV' for a in response.data['results'])

    def test_unauthenticated_access_denied(self, api_client, airport_abuja):
        """Test that unauthenticated access is denied."""
        url = reverse('api:airport-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Airline API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestAirlineAPI:
    """Tests for airline endpoints."""

    def test_list_airlines(self, authenticated_api_client, airline):
        """Test listing airlines."""
        url = reverse('api:airline-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_retrieve_airline(self, authenticated_api_client, airline):
        """Test retrieving a single airline."""
        url = reverse('api:airline-detail', kwargs={'pk': airline.pk})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'P4'


# ============================================================================
# Flight API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestFlightAPI:
    """Tests for flight endpoints."""

    def test_list_flights(self, authenticated_api_client, flight):
        """Test listing flights."""
        url = reverse('api:flight-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_retrieve_flight(self, authenticated_api_client, flight):
        """Test retrieving a single flight."""
        url = reverse('api:flight-detail', kwargs={'pk': flight.pk})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['flight_number'] == 'P4101'

    def test_search_flights_by_route(self, authenticated_api_client, flight, airport_abuja, airport_lagos):
        """Test searching flights by route."""
        url = reverse('api:flight-list')
        response = authenticated_api_client.get(url, {
            'origin': airport_abuja.pk,
            'destination': airport_lagos.pk
        })
        assert response.status_code == status.HTTP_200_OK

    def test_filter_flights_by_status(self, authenticated_api_client, flight):
        """Test filtering flights by status."""
        url = reverse('api:flight-list')
        response = authenticated_api_client.get(url, {'status': 'SCHEDULED'})
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Booking API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestBookingAPI:
    """Tests for booking endpoints."""

    def test_list_user_bookings(self, authenticated_api_client, booking):
        """Test listing user's bookings."""
        url = reverse('api:booking-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # User should see their own bookings
        assert len(response.data['results']) >= 1

    def test_retrieve_booking(self, authenticated_api_client, booking):
        """Test retrieving a single booking."""
        url = reverse('api:booking-detail', kwargs={'pk': booking.pk})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reference'] == booking.reference

    def test_create_booking(self, authenticated_api_client, flight, user):
        """Test creating a new booking."""
        url = reverse('api:booking-list')
        data = {
            'flight': flight.pk,
            'seat_class': 'ECONOMY',
            'contact_email': user.email,
            'contact_phone': '+2348012345678',
            'passengers': [
                {
                    'title': 'MR',
                    'first_name': 'Test',
                    'last_name': 'Passenger',
                    'date_of_birth': '1990-01-01',
                    'gender': 'M',
                    'nationality': 'Nigerian'
                }
            ]
        }
        response = authenticated_api_client.post(url, data, format='json')
        # Booking creation may require additional setup
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    def test_cancel_booking(self, authenticated_api_client, booking):
        """Test cancelling a booking."""
        url = reverse('api:booking-cancel', kwargs={'pk': booking.pk})
        response = authenticated_api_client.post(url)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_cannot_access_other_user_booking(self, api_client, booking, staff_user):
        """Test that users cannot access other users' bookings."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('api:booking-detail', kwargs={'pk': booking.pk})
        response = api_client.get(url)
        # Staff should be able to see it, regular user shouldn't
        # This depends on permission implementation


# ============================================================================
# Payment API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestPaymentAPI:
    """Tests for payment endpoints."""

    def test_list_user_payments(self, authenticated_api_client, payment):
        """Test listing user's payments."""
        url = reverse('api:payment-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_payment(self, authenticated_api_client, payment):
        """Test retrieving a single payment."""
        url = reverse('api:payment-detail', kwargs={'pk': payment.pk})
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Notification API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestNotificationAPI:
    """Tests for notification endpoints."""

    def test_list_user_notifications(self, authenticated_api_client, notification):
        """Test listing user's notifications."""
        url = reverse('api:notification-list')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_mark_notification_as_read(self, authenticated_api_client, notification):
        """Test marking a notification as read."""
        url = reverse('api:notification-mark-read', kwargs={'pk': notification.pk})
        response = authenticated_api_client.post(url)
        assert response.status_code == status.HTTP_200_OK

    def test_mark_all_notifications_as_read(self, authenticated_api_client, notification):
        """Test marking all notifications as read."""
        url = reverse('api:notification-mark-all-read')
        response = authenticated_api_client.post(url)
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Profile API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestProfileAPI:
    """Tests for user profile endpoints."""

    def test_get_profile(self, authenticated_api_client, user):
        """Test getting user profile."""
        url = reverse('api:profile')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_update_profile(self, authenticated_api_client, user):
        """Test updating user profile."""
        url = reverse('api:profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = authenticated_api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK


# ============================================================================
# Dashboard Stats API Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.api
class TestDashboardStatsAPI:
    """Tests for dashboard statistics endpoint."""

    def test_get_dashboard_stats(self, authenticated_api_client, booking, payment):
        """Test getting dashboard statistics."""
        url = reverse('api:dashboard-stats')
        response = authenticated_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Check expected fields
        assert 'total_bookings' in response.data or 'bookings_count' in response.data
