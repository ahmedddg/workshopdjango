from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    CONFIRMED = 'Confirmed', 'Confirmed'
    CANCELLED = 'Cancelled', 'Cancelled'


class Appointment(models.Model):
    reason = models.TextField()
    duration_minutes = models.DurationField()
    appointment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=status.choices, default=status.PENDING)
    doctor = models.ForeignKey('AccountApp.doctor', on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey('AccountApp.patient', on_delete=models.CASCADE, null=True, blank=True)
    prescription = models.FileField(
        upload_to='prescriptions/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                condition=~Q(status='Cancelled'),
                name='unique_doctor_appointment_date',
                violation_error_message="Ce médecin a déjà un rendez-vous à cette date et heure.",
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Valeur d'origine, pour détecter une modification de la date
        self._original_date = self.__dict__.get('appointment_date')

    def clean(self):
        super().clean()
        if not self.appointment_date:
            return
        date_changed = self._state.adding or self.appointment_date != self._original_date
        if date_changed and self.appointment_date <= timezone.now():
            raise ValidationError({'appointment_date': "La date du rendez-vous doit être dans le futur."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._original_date = self.appointment_date