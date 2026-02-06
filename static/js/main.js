/**
 * NAIA Airport Management System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initMobileMenu();
    initAlertDismiss();
    initFormValidation();
    initDatePickers();
    initPassengerCounter();
    initSeatSelection();
});

/**
 * Mobile Menu Toggle
 */
function initMobileMenu() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');

            // Toggle icon
            const icon = menuButton.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
    }
}

/**
 * Alert Message Auto-dismiss
 */
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.alert-message');

    alerts.forEach(function(alert) {
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Form Validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            // Validate required fields
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    showFieldError(field, 'This field is required');
                } else {
                    clearFieldError(field);
                }
            });

            // Validate email fields
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(function(field) {
                if (field.value && !isValidEmail(field.value)) {
                    isValid = false;
                    showFieldError(field, 'Please enter a valid email address');
                }
            });

            // Validate phone fields
            const phoneFields = form.querySelectorAll('input[type="tel"]');
            phoneFields.forEach(function(field) {
                if (field.value && !isValidPhone(field.value)) {
                    isValid = false;
                    showFieldError(field, 'Please enter a valid phone number');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function showFieldError(field, message) {
    field.classList.add('form-error');

    // Remove existing error message
    const existingError = field.parentElement.querySelector('.form-error-message');
    if (existingError) {
        existingError.remove();
    }

    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error-message';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('form-error');
    const errorMessage = field.parentElement.querySelector('.form-error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]{10,20}$/;
    return phoneRegex.test(phone);
}

/**
 * Date Picker Enhancement
 */
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');

    dateInputs.forEach(function(input) {
        // Set minimum date to today for departure dates
        if (input.classList.contains('departure-date') || input.name === 'departure_date') {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }

        // Handle return date minimum based on departure date
        if (input.classList.contains('return-date') || input.name === 'return_date') {
            const departureInput = document.querySelector('.departure-date, input[name="departure_date"]');
            if (departureInput) {
                departureInput.addEventListener('change', function() {
                    input.setAttribute('min', this.value);
                    if (input.value && input.value < this.value) {
                        input.value = this.value;
                    }
                });
            }
        }
    });
}

/**
 * Passenger Counter
 */
function initPassengerCounter() {
    const counters = document.querySelectorAll('.passenger-counter');

    counters.forEach(function(counter) {
        const decrementBtn = counter.querySelector('.decrement');
        const incrementBtn = counter.querySelector('.increment');
        const input = counter.querySelector('input');

        if (decrementBtn && incrementBtn && input) {
            const min = parseInt(input.getAttribute('min')) || 0;
            const max = parseInt(input.getAttribute('max')) || 9;

            decrementBtn.addEventListener('click', function() {
                let value = parseInt(input.value) || 0;
                if (value > min) {
                    input.value = value - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });

            incrementBtn.addEventListener('click', function() {
                let value = parseInt(input.value) || 0;
                if (value < max) {
                    input.value = value + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });

            // Update total passengers display if exists
            input.addEventListener('change', function() {
                updateTotalPassengers();
            });
        }
    });
}

function updateTotalPassengers() {
    const totalDisplay = document.getElementById('total-passengers');
    if (totalDisplay) {
        const adults = parseInt(document.querySelector('input[name="adults"]')?.value) || 0;
        const children = parseInt(document.querySelector('input[name="children"]')?.value) || 0;
        const infants = parseInt(document.querySelector('input[name="infants"]')?.value) || 0;
        totalDisplay.textContent = adults + children + infants;
    }
}

/**
 * Seat Selection
 */
function initSeatSelection() {
    const seatMap = document.querySelector('.seat-map');
    if (!seatMap) return;

    const seats = seatMap.querySelectorAll('.seat.available');
    const selectedSeatsInput = document.getElementById('selected-seats');
    const selectedSeatsDisplay = document.getElementById('selected-seats-display');
    const maxSeats = parseInt(seatMap.dataset.maxSeats) || 1;
    let selectedSeats = [];

    seats.forEach(function(seat) {
        seat.addEventListener('click', function() {
            const seatNumber = this.dataset.seat;

            if (this.classList.contains('selected')) {
                // Deselect seat
                this.classList.remove('selected');
                selectedSeats = selectedSeats.filter(s => s !== seatNumber);
            } else if (selectedSeats.length < maxSeats) {
                // Select seat
                this.classList.add('selected');
                selectedSeats.push(seatNumber);
            }

            // Update hidden input
            if (selectedSeatsInput) {
                selectedSeatsInput.value = selectedSeats.join(',');
            }

            // Update display
            if (selectedSeatsDisplay) {
                selectedSeatsDisplay.textContent = selectedSeats.length > 0
                    ? selectedSeats.join(', ')
                    : 'None selected';
            }
        });
    });
}

/**
 * Price Formatting
 */
function formatPrice(amount, currency = 'NGN') {
    return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Flight Search Form
 */
function swapAirports() {
    const origin = document.getElementById('origin');
    const destination = document.getElementById('destination');

    if (origin && destination) {
        const temp = origin.value;
        origin.value = destination.value;
        destination.value = temp;
    }
}

/**
 * Trip Type Toggle
 */
function toggleReturnDate() {
    const tripType = document.querySelector('input[name="trip_type"]:checked');
    const returnDateContainer = document.getElementById('return-date-container');

    if (returnDateContainer) {
        if (tripType && tripType.value === 'round_trip') {
            returnDateContainer.classList.remove('hidden');
            returnDateContainer.querySelector('input').setAttribute('required', 'required');
        } else {
            returnDateContainer.classList.add('hidden');
            returnDateContainer.querySelector('input').removeAttribute('required');
        }
    }
}

/**
 * Loading State
 */
function showLoading(button) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner mr-2"></span> Loading...';
}

function hideLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
}

/**
 * Confirmation Dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!');
    }).catch(function(err) {
        console.error('Failed to copy:', err);
    });
}

/**
 * Toast Notification
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 fade-in ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
    } text-white`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(function() {
        toast.style.opacity = '0';
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}

/**
 * Booking Reference Search
 */
function searchBookingReference() {
    const reference = document.getElementById('booking-reference');
    const lastName = document.getElementById('last-name');

    if (reference && lastName) {
        if (reference.value.length !== 6) {
            showFieldError(reference, 'Booking reference must be 6 characters');
            return false;
        }
        if (!lastName.value.trim()) {
            showFieldError(lastName, 'Please enter your last name');
            return false;
        }
        return true;
    }
    return false;
}
