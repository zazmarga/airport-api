from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Country


COUNTRY_URL = reverse("airport:country-list")


def sample_country(**params):
    defaults = {
        "name": "Argentina",
    }
    defaults.update(params)
    return Country.objects.create(**defaults)


class UnAuthenticatedCountryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        country = sample_country()
        response = self.client.post(COUNTRY_URL+f"{country.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

