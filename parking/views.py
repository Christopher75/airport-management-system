"""
Views for the Parking app.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, Min
from django.http import JsonResponse
from decimal import Decimal

from .models import (
    ParkingZone, ParkingSpot, ParkingPricing, ParkingReservation,
    ParkingService, ReservationService, ReservationStatus, VehicleType
)
from .forms import (
    ParkingSearchForm, ParkingReservationForm, CancelReservationForm
)


class ParkingHomeView(TemplateView):
    """Main parking page with search and zone overview."""
    template_name = 'parking/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParkingSearchForm()
        context['zones'] = ParkingZone.objects.filter(is_active=True).order_by('name')
        context['services'] = ParkingService.objects.filter(is_active=True)

        # Get featured zones (ones with special features)
        context['featured_zones'] = ParkingZone.objects.filter(
            is_active=True
        ).filter(
            Q(has_valet=True) | Q(has_ev_charging=True) | Q(is_covered=True)
        ).order_by('name')[:4]

        return context


class ParkingSearchView(ListView):
    """Search results for available parking."""
    template_name = 'parking/search_results.html'
    context_object_name = 'zones'

    def get_queryset(self):
        queryset = ParkingZone.objects.filter(
            is_active=True,
            available_spots__gt=0
        )

        # Apply filters
        vehicle_type = self.request.GET.get('vehicle_type')
        zone_type = self.request.GET.get('zone_type')

        if vehicle_type:
            queryset = queryset.filter(
                pricing__vehicle_type=vehicle_type,
                pricing__is_active=True
            ).distinct()

        if zone_type:
            queryset = queryset.filter(zone_type=zone_type)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParkingSearchForm(self.request.GET)
        context['check_in_date'] = self.request.GET.get('check_in_date')
        context['check_out_date'] = self.request.GET.get('check_out_date')
        context['vehicle_type'] = self.request.GET.get('vehicle_type', 'CAR')

        # Calculate prices for each zone
        check_in = self.request.GET.get('check_in_date')
        check_out = self.request.GET.get('check_out_date')

        if check_in and check_out:
            try:
                from datetime import datetime
                check_in_dt = datetime.fromisoformat(check_in)
                check_out_dt = datetime.fromisoformat(check_out)
                hours = (check_out_dt - check_in_dt).total_seconds() / 3600

                zone_prices = {}
                for zone in context['zones']:
                    pricing = zone.pricing.filter(
                        vehicle_type=context['vehicle_type'],
                        is_active=True
                    ).first()
                    if pricing:
                        zone_prices[zone.id] = pricing.calculate_price(hours, apply_online_discount=True)
                    else:
                        # Get default pricing
                        pricing = zone.pricing.filter(is_active=True).first()
                        if pricing:
                            zone_prices[zone.id] = pricing.calculate_price(hours, apply_online_discount=True)

                context['zone_prices'] = zone_prices
                context['duration_hours'] = hours
            except (ValueError, TypeError):
                pass

        return context


class ParkingZoneDetailView(DetailView):
    """Detail view for a parking zone."""
    model = ParkingZone
    template_name = 'parking/zone_detail.html'
    context_object_name = 'zone'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone = self.object

        # Get pricing
        context['pricing'] = zone.pricing.filter(is_active=True)

        # Get available services
        context['services'] = ParkingService.objects.filter(
            Q(available_zones=zone) | Q(available_zones__isnull=True),
            is_active=True
        ).distinct()

        # Get search parameters if present
        context['check_in_date'] = self.request.GET.get('check_in_date')
        context['check_out_date'] = self.request.GET.get('check_out_date')
        context['vehicle_type'] = self.request.GET.get('vehicle_type', 'CAR')

        return context


class CreateReservationView(LoginRequiredMixin, CreateView):
    """Create a parking reservation."""
    model = ParkingReservation
    form_class = ParkingReservationForm
    template_name = 'parking/create_reservation.html'

    def get_initial(self):
        initial = super().get_initial()

        # Pre-fill from search parameters
        zone_id = self.request.GET.get('zone')
        if zone_id:
            initial['zone'] = zone_id

        initial['check_in_date'] = self.request.GET.get('check_in_date')
        initial['check_out_date'] = self.request.GET.get('check_out_date')
        initial['vehicle_type'] = self.request.GET.get('vehicle_type', 'CAR')

        # Pre-fill contact from user
        if self.request.user.is_authenticated:
            initial['contact_email'] = self.request.user.email

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get zone if specified
        zone_id = self.request.GET.get('zone')
        if zone_id:
            context['selected_zone'] = get_object_or_404(ParkingZone, pk=zone_id)

        context['services'] = ParkingService.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        reservation = form.save(commit=False)
        reservation.user = self.request.user

        # Calculate pricing
        zone = reservation.zone
        vehicle_type = reservation.vehicle_type
        hours = reservation.get_duration_hours()

        pricing = zone.pricing.filter(
            vehicle_type=vehicle_type,
            is_active=True
        ).first()

        if not pricing:
            pricing = zone.pricing.filter(is_active=True).first()

        if pricing:
            base_price = pricing.calculate_price(hours, apply_online_discount=False)
            discount = base_price * (pricing.online_booking_discount / Decimal('100'))
            reservation.base_price = base_price
            reservation.discount_amount = discount
            reservation.total_price = base_price - discount
        else:
            # Default pricing if none set
            reservation.base_price = Decimal('500.00') * Decimal(str(hours))
            reservation.total_price = reservation.base_price

        reservation.save()

        # Add selected services
        services = form.cleaned_data.get('services', [])
        for service in services:
            ReservationService.objects.create(
                reservation=reservation,
                service=service,
                quantity=1,
                price=service.price
            )
            reservation.service_charges += service.price

        if services:
            reservation.total_price += reservation.service_charges
            reservation.save()

        messages.success(
            self.request,
            f'Parking reservation created successfully! Your reference: {reservation.reservation_code}'
        )

        return redirect('parking:reservation_detail', pk=reservation.pk)


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """View reservation details."""
    model = ParkingReservation
    template_name = 'parking/reservation_detail.html'
    context_object_name = 'reservation'

    def get_queryset(self):
        return ParkingReservation.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_form'] = CancelReservationForm()
        return context


class MyReservationsView(LoginRequiredMixin, ListView):
    """List user's parking reservations."""
    model = ParkingReservation
    template_name = 'parking/my_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 10

    def get_queryset(self):
        queryset = ParkingReservation.objects.filter(
            user=self.request.user
        ).select_related('zone').order_by('-created_at')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ReservationStatus.choices
        context['current_status'] = self.request.GET.get('status', '')

        # Count by status
        user_reservations = ParkingReservation.objects.filter(user=self.request.user)
        context['total_count'] = user_reservations.count()
        context['active_count'] = user_reservations.filter(
            status__in=[ReservationStatus.PENDING, ReservationStatus.CONFIRMED, ReservationStatus.ACTIVE]
        ).count()
        context['completed_count'] = user_reservations.filter(status=ReservationStatus.COMPLETED).count()

        return context


@login_required
def cancel_reservation(request, pk):
    """Cancel a parking reservation."""
    reservation = get_object_or_404(
        ParkingReservation,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':
        form = CancelReservationForm(request.POST)
        if form.is_valid():
            if reservation.can_cancel():
                reservation.status = ReservationStatus.CANCELLED
                reservation.admin_notes = f"Cancelled by user. Reason: {form.cleaned_data.get('reason', 'Not specified')}"
                reservation.save()

                messages.success(request, 'Your parking reservation has been cancelled.')
                return redirect('parking:my_reservations')
            else:
                messages.error(request, 'This reservation cannot be cancelled. Cancellation deadline has passed.')
        else:
            messages.error(request, 'Please confirm the cancellation.')

    return redirect('parking:reservation_detail', pk=pk)


class PricingView(TemplateView):
    """View all parking pricing."""
    template_name = 'parking/pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        zones = ParkingZone.objects.filter(is_active=True).prefetch_related('pricing')
        context['zones'] = zones

        # Group by zone type
        zone_types = {}
        for zone in zones:
            zone_type = zone.get_zone_type_display()
            if zone_type not in zone_types:
                zone_types[zone_type] = []
            zone_types[zone_type].append(zone)

        context['zone_types'] = zone_types
        context['vehicle_types'] = VehicleType.choices

        return context


class PayReservationView(LoginRequiredMixin, View):
    """Process payment for a parking reservation."""
    template_name = 'parking/payment.html'

    def get(self, request, pk):
        reservation = get_object_or_404(
            ParkingReservation,
            pk=pk,
            user=request.user
        )

        if reservation.is_paid:
            messages.info(request, 'This reservation has already been paid.')
            return redirect('parking:reservation_detail', pk=pk)

        if reservation.status == ReservationStatus.CANCELLED:
            messages.error(request, 'Cannot pay for a cancelled reservation.')
            return redirect('parking:reservation_detail', pk=pk)

        context = {
            'reservation': reservation,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        reservation = get_object_or_404(
            ParkingReservation,
            pk=pk,
            user=request.user
        )

        if reservation.is_paid:
            messages.info(request, 'This reservation has already been paid.')
            return redirect('parking:reservation_detail', pk=pk)

        payment_method = request.POST.get('payment_method', 'demo')

        if payment_method == 'demo':
            # Demo payment - instant confirmation
            reservation.is_paid = True
            reservation.paid_at = timezone.now()
            reservation.status = ReservationStatus.CONFIRMED
            reservation.payment_reference = f"DEMO-{reservation.reservation_code}"
            reservation.save()

            messages.success(request, 'Payment successful! Your parking reservation is confirmed.')
            return redirect('parking:reservation_detail', pk=pk)
        else:
            # Real payment via Paystack
            try:
                from payments.models import Payment, PaymentStatus, PaymentMethod
                from payments.services import paystack_service, PaystackError
                from django.urls import reverse

                # Create a payment record
                payment = Payment.objects.create(
                    user=request.user,
                    amount=reservation.total_price,
                    currency='NGN',
                    status=PaymentStatus.PENDING,
                    payment_method=PaymentMethod.CARD,
                    ip_address=self._get_client_ip(request),
                )

                # Store parking reservation reference
                payment.metadata = {'parking_reservation_id': reservation.pk}
                payment.save()

                # Build callback URL
                callback_url = request.build_absolute_uri(
                    reverse('parking:verify_payment', kwargs={'pk': reservation.pk, 'payment_ref': payment.paystack_reference})
                )

                # Initialize Paystack transaction
                result = paystack_service.initialize_transaction(payment, callback_url)

                return redirect(result['authorization_url'])

            except Exception as e:
                messages.error(request, f'Payment initialization failed. Please try again.')
                return redirect('parking:pay_reservation', pk=pk)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


@login_required
def verify_parking_payment(request, pk, payment_ref):
    """Verify parking payment callback from Paystack."""
    reservation = get_object_or_404(
        ParkingReservation,
        pk=pk,
        user=request.user
    )

    try:
        from payments.models import Payment, PaymentStatus
        from payments.services import paystack_service

        payment = Payment.objects.get(paystack_reference=payment_ref)

        # Verify with Paystack
        result = paystack_service.verify_transaction(payment_ref)

        if result.get('status') == 'success':
            payment.status = PaymentStatus.COMPLETED
            payment.paid_at = timezone.now()
            payment.save()

            reservation.is_paid = True
            reservation.paid_at = timezone.now()
            reservation.status = ReservationStatus.CONFIRMED
            reservation.payment_reference = payment_ref
            reservation.save()

            messages.success(request, 'Payment successful! Your parking reservation is confirmed.')
        else:
            payment.status = PaymentStatus.FAILED
            payment.save()
            messages.error(request, 'Payment verification failed. Please contact support.')

    except Exception as e:
        messages.error(request, 'Payment verification error. Please contact support.')

    return redirect('parking:reservation_detail', pk=pk)


def get_price_estimate(request):
    """AJAX endpoint to get price estimate."""
    zone_id = request.GET.get('zone')
    vehicle_type = request.GET.get('vehicle_type', 'CAR')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if not all([zone_id, check_in, check_out]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        zone = ParkingZone.objects.get(pk=zone_id)
        from datetime import datetime
        check_in_dt = datetime.fromisoformat(check_in)
        check_out_dt = datetime.fromisoformat(check_out)
        hours = (check_out_dt - check_in_dt).total_seconds() / 3600

        pricing = zone.pricing.filter(
            vehicle_type=vehicle_type,
            is_active=True
        ).first() or zone.pricing.filter(is_active=True).first()

        if pricing:
            base_price = pricing.calculate_price(hours, apply_online_discount=False)
            discounted_price = pricing.calculate_price(hours, apply_online_discount=True)
            discount = base_price - discounted_price

            return JsonResponse({
                'base_price': float(base_price),
                'discount': float(discount),
                'total_price': float(discounted_price),
                'duration_hours': round(hours, 1),
                'online_discount_percent': float(pricing.online_booking_discount)
            })
        else:
            return JsonResponse({'error': 'Pricing not available'}, status=404)

    except (ParkingZone.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)
