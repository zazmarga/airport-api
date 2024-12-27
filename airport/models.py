from django.core.validators import RegexValidator
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=63, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self) -> str:  # noqa: ANN101
        return self.name


class City(models.Model):
    name = models.CharField(max_length=63)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
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
                code="invalid_code_iata"
            )
        ],
        null=False
    )
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    )

    def __str__(self) -> str:  # noqa: ANN101
        return self.cod_iata

    @property
    def full_name(self) -> str:  # noqa: ANN101
        return f"{self.cod_iata}: {self.name} ({self.closest_big_city.name})"
