from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


def validate_past_date(value):
    if value >= timezone.localdate():
        raise ValidationError("La date de naissance doit être dans le passé.")


digits_8 = RegexValidator(r"^\d{8}$", "Ce champ doit contenir exactement 8 chiffres.")


class user(AbstractUser):
    pass


class doctor(user):
    phone = models.CharField(max_length=8, validators=[digits_8])
    licence_number = models.CharField(
        max_length=6,
        unique=True,
        validators=[MinLengthValidator(6, "Le numéro d'inscription doit contenir exactement 6 caractères.")],
    )
    specialities = models.ManyToManyField('Speciality', related_name='doctors', blank=True)


class patient(user):
    phone = models.CharField(max_length=8, validators=[digits_8])
    birth_date = models.DateField(validators=[validate_past_date])
    national_id = models.CharField(max_length=8, unique=True, validators=[digits_8])


class Speciality(models.Model):
    name = models.CharField(max_length=100)