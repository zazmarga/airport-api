import pathlib
import uuid

import pytz
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

from app import settings


class Country(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=63)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self) -> str:
        # return f"{self.name} ({self.country.name})"
        return self.name


class AirportTimeZone(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=100)
    cod_iata = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex="^[A-Z]{3}$",
                message="Code IATA must be exactly 3 uppercase letters",
                code="invalid_code_iata",
            )
        ],
        null=False,
    )
    closest_big_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="airports"
    )
    time_zone = models.ForeignKey(
        AirportTimeZone, on_delete=models.CASCADE, related_name="airports"
    )

    def __str__(self) -> str:
        return self.cod_iata

    @property
    def full_name(self) -> str:
        return (f"{self.cod_iata}: {self.name} "
                f"({self.closest_big_city.name} - "
                f"{self.closest_big_city.country.name})")


class Role(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="crews"
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}: {self.role.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name_plural = "airplane types"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


def logo_image_path(instance: "AirlineCompany", filename: str) -> pathlib.Path:
    file_suffix = pathlib.Path(filename).suffix
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}" + file_suffix
    return pathlib.Path("upload/logos/") / pathlib.Path(filename)


class AirlineCompany(models.Model):
    name = models.CharField(max_length=63)
    registration_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    logo = models.ImageField(null=True, blank=True, upload_to=logo_image_path)

    class Meta:
        verbose_name_plural = "airline companies"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "facilities"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE
    )
    airline_company = models.ForeignKey(
        AirlineCompany, on_delete=models.CASCADE
    )
    facilities = models.ManyToManyField(
        Facility, related_name="airplanes", blank=True
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_routes"
    )
    distance = models.IntegerField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "source",
                    "destination",
                ]
            ),
        ]

    def __str__(self) -> str:
        return f"{self.source} - {self.destination}"


class Flight(models.Model):
    name = models.CharField(max_length=24)
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew_members = models.ManyToManyField(Crew, related_name="flights")
    departure_time_utc = models.DateTimeField(editable=False)
    arrival_time_utc = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        departure_time_utc = self.departure_time.replace(
            tzinfo=pytz.timezone(self.route.source.time_zone.name)
        )
        arrival_time_utc = self.arrival_time.replace(
            tzinfo=pytz.timezone(self.route.destination.time_zone.name)
        )
        self.departure_time_utc = departure_time_utc.astimezone(pytz.utc)
        self.arrival_time_utc = arrival_time_utc.astimezone(pytz.utc)
        super().save(*args, **kwargs)

    @property
    def duration(self) -> str:
        if self.departure_time_utc and self.arrival_time_utc:
            duration = self.arrival_time_utc - self.departure_time_utc

            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)

            return f"{int(hours)}h {int(minutes)}m"
        return "Duration not available"

    def __str__(self) -> str:
        return self.name


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.CharField(max_length=1)
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        # validation on level model & serializer too
        unique_together = (
            ("flight", "row", "seat"),
        )
        ordering = ("row", "seat", )

    def __str__(self) -> str:
        return f"{self.flight.name} (row: {self.row}, seat: {self.seat})"

    @staticmethod
    def validate_ticket(
            row: int, num_rows: int,
            seat: str, num_seats: int,
            error_to_raise
    ):
        # Modern airplanes can have no more than 10 seats in a row,
        # designated by the appropriate letters:
        seats_set = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]
        seats_set = seats_set[:num_seats]
        if not (seat in seats_set):
            raise error_to_raise(
                {
                    "seat": "seat must be indicated by a letter "
                    f"from the set {seats_set}, "
                    f"not seat={seat}",
                }
            )
        if not (1 <= row <= num_rows):
            raise error_to_raise(
                {
                    "row": "number must be in available range: "
                    f"1 to {num_rows}, "
                    f"not row={row}",
                }
            )

    def clean(self) -> None:
        Ticket.validate_ticket(
            self.row,
            self.flight.airplane.rows,
            self.seat,
            self.flight.airplane.seats_in_row,
            ValueError)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Ticket, self).save(*args, **kwargs)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.created_at)
