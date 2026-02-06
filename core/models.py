"""
Core abstract models for the Airport Management System.

Provides base classes that other models inherit from for consistent
timestamp tracking and UUID primary keys.
"""

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created_at and updated_at fields.

    All models that need timestamp tracking should inherit from this class.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the record was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the record was last updated",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as primary key instead of auto-incrementing integer.

    Use this for models where you want non-sequential, unpredictable primary keys,
    such as bookings, payments, and other sensitive records.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record",
    )

    class Meta:
        abstract = True


class TimeStampedUUIDModel(TimeStampedModel, UUIDModel):
    """
    Abstract base model combining UUID primary key with timestamp tracking.

    Use this for models that need both features, such as bookings and payments.
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]
