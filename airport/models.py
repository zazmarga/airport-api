import pathlib
import uuid

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
