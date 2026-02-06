"""
E-Ticket PDF generation service.

Generates professional PDF e-tickets for confirmed bookings.
"""

import io
import os
from datetime import datetime

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)
from reportlab.graphics.barcode import code128


class ETicketGenerator:
    """
    Generates PDF e-tickets for flight bookings.
    """

    # NAIA brand colors
    NAIA_GREEN = colors.Color(0/255, 166/255, 81/255)  # #00A651
    NAIA_DARK = colors.Color(26/255, 26/255, 46/255)   # #1a1a2e

    def __init__(self, booking):
        """Initialize with a booking instance."""
        self.booking = booking
        self.flight = booking.flight
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='TicketTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.NAIA_GREEN,
            spaceAfter=20,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.NAIA_DARK,
            spaceBefore=15,
            spaceAfter=10,
        ))
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
        ))
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
        ))
        self.styles.add(ParagraphStyle(
            name='Important',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            spaceBefore=10,
        ))

    def generate(self):
        """
        Generate the e-ticket PDF.

        Returns:
            BytesIO: PDF buffer ready to be written or served.
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Build the document content
        elements = []

        # Header
        elements.extend(self._build_header())

        # Booking Reference Section
        elements.extend(self._build_booking_reference())

        # Flight Details
        elements.extend(self._build_flight_details())

        # Passenger Details
        elements.extend(self._build_passenger_details())

        # Barcode
        elements.extend(self._build_barcode())

        # Important Information
        elements.extend(self._build_important_info())

        # Footer
        elements.extend(self._build_footer())

        # Build the PDF
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer

    def _build_header(self):
        """Build the ticket header with logo and title."""
        elements = []

        # Header table with logo and airport name
        header_data = [
            [
                Paragraph('<font color="#00A651" size="28"><b>NAIA</b></font>', self.styles['Normal']),
                Paragraph('''
                    <font size="12"><b>Nnamdi Azikiwe International Airport</b></font><br/>
                    <font size="9" color="gray">Abuja, Nigeria</font>
                ''', self.styles['Normal']),
                Paragraph('<font size="16" color="#00A651"><b>E-TICKET</b></font>', self.styles['Normal'])
            ]
        ]

        header_table = Table(header_data, colWidths=[60*mm, 80*mm, 40*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 5*mm))

        # Divider line
        line_data = [['']]
        line_table = Table(line_data, colWidths=[170*mm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.NAIA_GREEN),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 5*mm))

        return elements

    def _build_booking_reference(self):
        """Build the booking reference section."""
        elements = []

        # Large booking reference display
        ref_data = [
            [
                Paragraph('<font size="10" color="gray">Booking Reference</font>', self.styles['Normal']),
                Paragraph('<font size="10" color="gray">Status</font>', self.styles['Normal']),
                Paragraph('<font size="10" color="gray">Class</font>', self.styles['Normal']),
            ],
            [
                Paragraph(f'<font size="28" color="#00A651"><b>{self.booking.reference}</b></font>', self.styles['Normal']),
                Paragraph(f'<font size="14"><b>{self.booking.get_status_display()}</b></font>', self.styles['Normal']),
                Paragraph(f'<font size="14"><b>{self.booking.get_seat_class_display()}</b></font>', self.styles['Normal']),
            ]
        ]

        ref_table = Table(ref_data, colWidths=[60*mm, 55*mm, 55*mm])
        ref_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.97, 0.97, 0.97)),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(ref_table)
        elements.append(Spacer(1, 8*mm))

        return elements

    def _build_flight_details(self):
        """Build the flight details section."""
        elements = []

        elements.append(Paragraph('<b>FLIGHT DETAILS</b>', self.styles['SectionHeader']))

        # Flight info row
        flight_data = [
            [
                # Flight number and airline
                [
                    Paragraph('<font size="9" color="gray">Flight</font>', self.styles['Normal']),
                    Paragraph(f'<font size="18"><b>{self.flight.flight_number}</b></font>', self.styles['Normal']),
                    Paragraph(f'<font size="9">{self.flight.airline.name}</font>', self.styles['Normal']),
                ],
                # From
                [
                    Paragraph('<font size="9" color="gray">From</font>', self.styles['Normal']),
                    Paragraph(f'<font size="22"><b>{self.flight.origin.code}</b></font>', self.styles['Normal']),
                    Paragraph(f'<font size="9">{self.flight.origin.city}</font>', self.styles['Normal']),
                ],
                # Arrow
                [
                    Paragraph('', self.styles['Normal']),
                    Paragraph('<font size="20" color="#00A651">&#10132;</font>', self.styles['Normal']),
                    Paragraph('', self.styles['Normal']),
                ],
                # To
                [
                    Paragraph('<font size="9" color="gray">To</font>', self.styles['Normal']),
                    Paragraph(f'<font size="22"><b>{self.flight.destination.code}</b></font>', self.styles['Normal']),
                    Paragraph(f'<font size="9">{self.flight.destination.city}</font>', self.styles['Normal']),
                ],
                # Duration
                [
                    Paragraph('<font size="9" color="gray">Duration</font>', self.styles['Normal']),
                    Paragraph(f'<font size="14"><b>{self.flight.duration or "N/A"}</b></font>', self.styles['Normal']),
                    Paragraph('', self.styles['Normal']),
                ],
            ]
        ]

        flight_table = Table(flight_data, colWidths=[35*mm, 40*mm, 20*mm, 40*mm, 35*mm])
        flight_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(flight_table)
        elements.append(Spacer(1, 3*mm))

        # Departure and Arrival times
        time_data = [
            [
                Paragraph('<font size="9" color="gray">Departure Date & Time</font>', self.styles['Normal']),
                Paragraph('<font size="9" color="gray">Arrival Date & Time</font>', self.styles['Normal']),
                Paragraph('<font size="9" color="gray">Gate</font>', self.styles['Normal']),
            ],
            [
                Paragraph(f'''<font size="12"><b>{self.flight.scheduled_departure.strftime("%a, %d %b %Y")}</b></font><br/>
                              <font size="16" color="#00A651"><b>{self.flight.scheduled_departure.strftime("%H:%M")}</b></font>''',
                          self.styles['Normal']),
                Paragraph(f'''<font size="12"><b>{self.flight.scheduled_arrival.strftime("%a, %d %b %Y")}</b></font><br/>
                              <font size="16"><b>{self.flight.scheduled_arrival.strftime("%H:%M")}</b></font>''',
                          self.styles['Normal']),
                Paragraph(f'''<font size="16"><b>{self.flight.departure_gate.terminal if self.flight.departure_gate else "TBA"}{self.flight.departure_gate.gate_number if self.flight.departure_gate else ""}</b></font>''',
                          self.styles['Normal']),
            ]
        ]

        time_table = Table(time_data, colWidths=[60*mm, 60*mm, 50*mm])
        time_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(time_table)
        elements.append(Spacer(1, 8*mm))

        return elements

    def _build_passenger_details(self):
        """Build the passenger details section."""
        elements = []

        elements.append(Paragraph('<b>PASSENGER DETAILS</b>', self.styles['SectionHeader']))

        passengers = self.booking.passengers.all()

        for i, passenger in enumerate(passengers, 1):
            pax_data = [
                [
                    Paragraph(f'<font size="9" color="gray">Passenger {i}</font>', self.styles['Normal']),
                    Paragraph('<font size="9" color="gray">Seat</font>', self.styles['Normal']),
                    Paragraph('<font size="9" color="gray">Type</font>', self.styles['Normal']),
                    Paragraph('<font size="9" color="gray">Baggage</font>', self.styles['Normal']),
                ],
                [
                    Paragraph(f'<font size="12"><b>{passenger.full_name}</b></font>', self.styles['Normal']),
                    Paragraph(f'<font size="14" color="#00A651"><b>{passenger.seat_number or "TBA"}</b></font>', self.styles['Normal']),
                    Paragraph(f'<font size="10">{passenger.get_passenger_type_display()}</font>', self.styles['Normal']),
                    Paragraph(f'<font size="10">{passenger.checked_baggage} kg</font>', self.styles['Normal']),
                ]
            ]

            pax_table = Table(pax_data, colWidths=[70*mm, 35*mm, 35*mm, 30*mm])
            pax_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white if i % 2 == 0 else colors.Color(0.98, 0.98, 0.98)),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
            ]))
            elements.append(pax_table)
            elements.append(Spacer(1, 2*mm))

        elements.append(Spacer(1, 5*mm))
        return elements

    def _build_barcode(self):
        """Build the barcode section."""
        elements = []

        # Generate barcode data: REFERENCE-FLIGHT-DATE
        barcode_data = f"{self.booking.reference}-{self.flight.flight_number}-{self.flight.scheduled_departure.strftime('%Y%m%d')}"

        # Create barcode
        try:
            barcode = code128.Code128(barcode_data, barWidth=0.5*mm, barHeight=15*mm)

            barcode_table = Table([[barcode]], colWidths=[170*mm])
            barcode_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(barcode_table)

            # Barcode text
            elements.append(Paragraph(
                f'<font size="8" color="gray">{barcode_data}</font>',
                ParagraphStyle('BarcodeText', parent=self.styles['Normal'], alignment=1)
            ))
        except Exception:
            # If barcode generation fails, just show the reference
            elements.append(Paragraph(
                f'<font size="12"><b>{barcode_data}</b></font>',
                ParagraphStyle('BarcodeText', parent=self.styles['Normal'], alignment=1)
            ))

        elements.append(Spacer(1, 8*mm))
        return elements

    def _build_important_info(self):
        """Build the important information section."""
        elements = []

        elements.append(Paragraph('<b>IMPORTANT INFORMATION</b>', self.styles['SectionHeader']))

        info_text = """
        <font size="9">
        <b>1. Check-in:</b> Online check-in opens 24 hours before departure. Airport check-in counters close 45 minutes before departure.<br/><br/>
        <b>2. Documents:</b> Please ensure you have valid identification and travel documents. For international flights, a valid passport with at least 6 months validity is required.<br/><br/>
        <b>3. Baggage:</b> Your checked baggage allowance is shown above. Excess baggage fees may apply.<br/><br/>
        <b>4. Security:</b> Please arrive at the airport at least 2 hours before departure for domestic flights and 3 hours for international flights.<br/><br/>
        <b>5. Contact:</b> For flight status and assistance, call +234 9 123 4567 or visit www.naiaabuja.gov.ng
        </font>
        """
        elements.append(Paragraph(info_text, self.styles['Normal']))
        elements.append(Spacer(1, 10*mm))

        return elements

    def _build_footer(self):
        """Build the ticket footer."""
        elements = []

        # Divider
        line_data = [['']]
        line_table = Table(line_data, colWidths=[170*mm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.lightgrey),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 3*mm))

        # Footer text
        footer_text = f"""
        <font size="8" color="gray">
        This e-ticket was generated on {datetime.now().strftime("%d %b %Y at %H:%M")}.<br/>
        Booking Reference: {self.booking.reference} | Contact: {self.booking.contact_email or self.booking.user.email}<br/>
        Nnamdi Azikiwe International Airport - Abuja, Nigeria | www.naiaabuja.gov.ng
        </font>
        """
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer', parent=self.styles['Normal'], alignment=1
        )))

        return elements


def generate_eticket_pdf(booking):
    """
    Generate a PDF e-ticket for a booking.

    Args:
        booking: Booking instance

    Returns:
        BytesIO: PDF buffer
    """
    generator = ETicketGenerator(booking)
    return generator.generate()
