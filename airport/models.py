import pathlib
import uuid
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self) -> str:  # noqa: ANN101
        return self.name


class City(models.Model):
    name = models.CharField(max_length=63)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:  # noqa: ANN101
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

    def __str__(self) -> str:  # noqa: ANN101
        return self.cod_iata

    @property
    def full_name(self) -> str:  # noqa: ANN101
        return f"{self.cod_iata}: {self.name} ({self.closest_big_city.name})"


class Role(models.Model):
    name = models.CharField(max_length=63, unique=True)

    def __str__(self) -> str:  # noqa: ANN101
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self) -> str:  # noqa: ANN101
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name_plural = "airplane types"

    def __str__(self) -> str:  # noqa: ANN101
        return self.name


def logo_image_path(instance: "AirlineCompany", filename: str) -> pathlib.Path:
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}"
    filename += pathlib.Path(filename).suffix
    return pathlib.Path("upload/logos/") / pathlib.Path(filename)


class AirlineCompany(models.Model):
    name = models.CharField(max_length=63)
    registration_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    logo = models.ImageField(null=True, blank=True, upload_to=logo_image_path)

    class Meta:
        verbose_name_plural = "airline companies"

    def __str__(self) -> str:  # noqa: ANN101
        return f"{self.name} ({self.registration_country.name})"


class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "facilities"

    def __str__(self) -> str:  # noqa: ANN101
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
    def capacity(self) -> int:  # noqa: ANN101
        return self.rows * self.seats_in_row

    def __str__(self) -> str:  # noqa: ANN101
        return f"{self.name} ({self.airplane_type.name})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes"
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

    def __str__(self) -> str:  # noqa: ANN101
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

    @property
    def duration(self) -> str:  # noqa: ANN101
        geolocator = Nominatim(user_agent="flight_duration_calculator")
        tf = TimezoneFinder()
        # Getting airport coordinates
        departure_location = geolocator.geocode(
            f"{self.route.source.closest_big_city.name}, "
            f"{self.route.source.closest_big_city.country.name}"
        )
        arrival_location = geolocator.geocode(
            f"{self.route.destination.closest_big_city.name}, "
            f"{self.route.destination.closest_big_city.country.name}"
        )
        # Definition of time zones
        departure_timezone = pytz.timezone(
            tf.timezone_at(
                lat=departure_location.latitude,
                lng=departure_location.longitude
            )
        )
        arrival_timezone = pytz.timezone(
            tf.timezone_at(
                lat=arrival_location.latitude,
                lng=arrival_location.longitude
            )
        )
        # Convert departure and arrival times to the appropriate time zones
        departure_time = self.departure_time.astimezone(departure_timezone)
        arrival_time = self.arrival_time.astimezone(arrival_timezone)
        # Calculating flight duration in seconds
        duration = arrival_time - departure_time
        # Converting flight duration to hours and minutes
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        return f"{int(hours)}h {int(minutes)}m"

    def __str__(self) -> str:  # noqa: ANN101
        return f"{self.name} ({self.departure_time})"
