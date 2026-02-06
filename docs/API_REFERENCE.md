# API Reference

Complete API documentation for the NAIA Airport Management System.

**Base URL**: `https://yourdomain.com/api/v1/`

**Interactive Documentation**:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Obtain Token

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response (200 OK)**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK)**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Verify Token

```http
POST /api/v1/auth/token/verify/
Content-Type: application/json

{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Authentication

Include the access token in the Authorization header:

```http
GET /api/v1/bookings/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## User Registration

### Register New User

```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created)**:
```json
{
    "id": 1,
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "message": "Registration successful. Please verify your email."
}
```

---

## User Profile

### Get Profile

```http
GET /api/v1/profile/
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+2348012345678",
    "date_of_birth": "1990-01-15",
    "nationality": "Nigerian",
    "passport_number": "A12345678",
    "profile": {
        "loyalty_points": 1500,
        "loyalty_tier": "SILVER"
    }
}
```

### Update Profile

```http
PATCH /api/v1/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
    "first_name": "Jonathan",
    "phone_number": "+2348012345679"
}
```

---

## Airports

### List Airports

```http
GET /api/v1/airports/
Authorization: Bearer <token>
```

**Query Parameters**:
- `search` - Search by name, code, or city
- `country` - Filter by country
- `is_active` - Filter by active status (true/false)

**Response (200 OK)**:
```json
{
    "count": 25,
    "next": "http://api.example.com/airports/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "code": "ABV",
            "name": "Nnamdi Azikiwe International Airport",
            "city": "Abuja",
            "country": "Nigeria",
            "timezone": "Africa/Lagos",
            "is_active": true
        },
        {
            "id": 2,
            "code": "LOS",
            "name": "Murtala Muhammed International Airport",
            "city": "Lagos",
            "country": "Nigeria",
            "timezone": "Africa/Lagos",
            "is_active": true
        }
    ]
}
```

### Get Airport Details

```http
GET /api/v1/airports/{id}/
Authorization: Bearer <token>
```

---

## Airlines

### List Airlines

```http
GET /api/v1/airlines/
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Air Peace",
            "code": "P4",
            "country": "Nigeria",
            "logo_url": "https://example.com/airpeace-logo.png",
            "is_active": true
        }
    ]
}
```

---

## Flights

### List Flights

```http
GET /api/v1/flights/
Authorization: Bearer <token>
```

**Query Parameters**:
- `origin` - Origin airport ID
- `destination` - Destination airport ID
- `departure_date` - Departure date (YYYY-MM-DD)
- `status` - Flight status (SCHEDULED, BOARDING, DEPARTED, etc.)
- `airline` - Airline ID
- `min_price` - Minimum price
- `max_price` - Maximum price
- `ordering` - Sort by field (e.g., `-scheduled_departure`)

**Example**:
```http
GET /api/v1/flights/?origin=1&destination=2&departure_date=2024-03-15&status=SCHEDULED
```

**Response (200 OK)**:
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "flight_number": "P4101",
            "airline": {
                "id": 1,
                "name": "Air Peace",
                "code": "P4"
            },
            "origin": {
                "id": 1,
                "code": "ABV",
                "city": "Abuja"
            },
            "destination": {
                "id": 2,
                "code": "LOS",
                "city": "Lagos"
            },
            "scheduled_departure": "2024-03-15T08:00:00Z",
            "scheduled_arrival": "2024-03-15T09:15:00Z",
            "status": "SCHEDULED",
            "economy_price": "35000.00",
            "business_price": "85000.00",
            "first_class_price": "150000.00",
            "available_seats": 120,
            "gate": "A1"
        }
    ]
}
```

### Get Flight Details

```http
GET /api/v1/flights/{id}/
Authorization: Bearer <token>
```

### Get Flight Status

```http
GET /api/v1/flights/{id}/status/
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
    "flight_number": "P4101",
    "status": "BOARDING",
    "gate": "A1",
    "scheduled_departure": "2024-03-15T08:00:00Z",
    "estimated_departure": "2024-03-15T08:10:00Z",
    "actual_departure": null,
    "delay_minutes": 10,
    "remarks": "Boarding in progress"
}
```

---

## Bookings

### List User Bookings

```http
GET /api/v1/bookings/
Authorization: Bearer <token>
```

**Query Parameters**:
- `status` - Filter by status (PENDING, CONFIRMED, CANCELLED)
- `ordering` - Sort by field

**Response (200 OK)**:
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "reference": "ABC123",
            "flight": {
                "id": 1,
                "flight_number": "P4101",
                "origin": {"code": "ABV", "city": "Abuja"},
                "destination": {"code": "LOS", "city": "Lagos"},
                "scheduled_departure": "2024-03-15T08:00:00Z"
            },
            "status": "CONFIRMED",
            "seat_class": "ECONOMY",
            "total_price": "40500.00",
            "created_at": "2024-03-01T10:30:00Z",
            "passengers_count": 1
        }
    ]
}
```

### Get Booking Details

```http
GET /api/v1/bookings/{id}/
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
    "id": 1,
    "reference": "ABC123",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe"
    },
    "flight": {
        "id": 1,
        "flight_number": "P4101",
        "airline": {"name": "Air Peace", "code": "P4"},
        "origin": {"code": "ABV", "city": "Abuja", "name": "Nnamdi Azikiwe International Airport"},
        "destination": {"code": "LOS", "city": "Lagos", "name": "Murtala Muhammed International Airport"},
        "scheduled_departure": "2024-03-15T08:00:00Z",
        "scheduled_arrival": "2024-03-15T09:15:00Z"
    },
    "status": "CONFIRMED",
    "seat_class": "ECONOMY",
    "contact_email": "user@example.com",
    "contact_phone": "+2348012345678",
    "base_price": "35000.00",
    "taxes": "3500.00",
    "fees": "2000.00",
    "discount": "0.00",
    "total_price": "40500.00",
    "passengers": [
        {
            "id": 1,
            "title": "MR",
            "first_name": "John",
            "last_name": "Doe",
            "gender": "M",
            "date_of_birth": "1990-01-15",
            "nationality": "Nigerian",
            "passport_number": "A12345678",
            "seat_number": "12A"
        }
    ],
    "created_at": "2024-03-01T10:30:00Z",
    "confirmed_at": "2024-03-01T10:35:00Z"
}
```

### Create Booking

```http
POST /api/v1/bookings/
Authorization: Bearer <token>
Content-Type: application/json

{
    "flight": 1,
    "seat_class": "ECONOMY",
    "contact_email": "user@example.com",
    "contact_phone": "+2348012345678",
    "passengers": [
        {
            "title": "MR",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "gender": "M",
            "nationality": "Nigerian",
            "passport_number": "A12345678",
            "email": "john.doe@example.com",
            "phone": "+2348012345678"
        }
    ]
}
```

**Response (201 Created)**:
```json
{
    "id": 1,
    "reference": "ABC123",
    "status": "PENDING",
    "total_price": "40500.00",
    "message": "Booking created. Please complete payment within 30 minutes."
}
```

### Cancel Booking

```http
POST /api/v1/bookings/{id}/cancel/
Authorization: Bearer <token>
Content-Type: application/json

{
    "reason": "Change of plans"
}
```

**Response (200 OK)**:
```json
{
    "message": "Booking cancelled successfully",
    "refund_amount": "38500.00",
    "refund_status": "Processing"
}
```

---

## Payments

### List Payments

```http
GET /api/v1/payments/
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "booking_reference": "ABC123",
            "amount": "40500.00",
            "currency": "NGN",
            "status": "COMPLETED",
            "payment_method": "CARD",
            "reference": "PAY-ABC123",
            "paid_at": "2024-03-01T10:35:00Z"
        }
    ]
}
```

### Initialize Payment

```http
POST /api/v1/payments/initialize/
Authorization: Bearer <token>
Content-Type: application/json

{
    "booking_id": 1
}
```

**Response (200 OK)**:
```json
{
    "authorization_url": "https://checkout.paystack.com/xxxxx",
    "access_code": "xxxxx",
    "reference": "PAY-ABC123"
}
```

### Verify Payment

```http
GET /api/v1/payments/verify/{reference}/
Authorization: Bearer <token>
```

---

## Notifications

### List Notifications

```http
GET /api/v1/notifications/
Authorization: Bearer <token>
```

**Query Parameters**:
- `is_read` - Filter by read status (true/false)
- `type` - Notification type

**Response (200 OK)**:
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "type": "BOOKING_CONFIRMATION",
            "title": "Booking Confirmed",
            "message": "Your booking ABC123 has been confirmed.",
            "is_read": false,
            "created_at": "2024-03-01T10:35:00Z"
        }
    ]
}
```

### Mark as Read

```http
POST /api/v1/notifications/{id}/mark-read/
Authorization: Bearer <token>
```

### Mark All as Read

```http
POST /api/v1/notifications/mark-all-read/
Authorization: Bearer <token>
```

---

## Dashboard Statistics

### Get User Dashboard Stats

```http
GET /api/v1/dashboard/stats/
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
    "total_bookings": 5,
    "upcoming_flights": 2,
    "loyalty_points": 1500,
    "loyalty_tier": "SILVER",
    "recent_bookings": [
        {
            "reference": "ABC123",
            "flight_number": "P4101",
            "departure": "2024-03-15T08:00:00Z",
            "status": "CONFIRMED"
        }
    ],
    "notifications_count": 3
}
```

---

## Error Responses

### 400 Bad Request

```json
{
    "error": "validation_error",
    "message": "Invalid input data",
    "details": {
        "email": ["This field is required."],
        "password": ["Password must be at least 8 characters."]
    }
}
```

### 401 Unauthorized

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
    "detail": "Not found."
}
```

### 429 Too Many Requests

```json
{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

### 500 Internal Server Error

```json
{
    "error": "server_error",
    "message": "An unexpected error occurred. Please try again later."
}
```

---

## Rate Limits

| Endpoint Type | Anonymous | Authenticated |
|---------------|-----------|---------------|
| General API | 100/hour | 1000/hour |
| Authentication | 5/minute | N/A |
| Booking Creation | N/A | 10/hour |
| Payment Initialization | N/A | 20/hour |

---

## Pagination

All list endpoints return paginated results:

```json
{
    "count": 100,
    "next": "https://api.example.com/endpoint/?page=2",
    "previous": null,
    "results": [...]
}
```

**Query Parameters**:
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 20, max: 100)

---

## Webhook Events

### Payment Completed

```json
{
    "event": "payment.completed",
    "data": {
        "reference": "PAY-ABC123",
        "booking_reference": "ABC123",
        "amount": 40500,
        "currency": "NGN",
        "paid_at": "2024-03-01T10:35:00Z"
    }
}
```

### Flight Status Changed

```json
{
    "event": "flight.status_changed",
    "data": {
        "flight_number": "P4101",
        "old_status": "SCHEDULED",
        "new_status": "DELAYED",
        "delay_minutes": 30,
        "affected_bookings": ["ABC123", "DEF456"]
    }
}
```

---

**Last Updated**: 2024
