from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Country,
    City,
    AirportTimeZone,
    Airport,
)
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    CityListSerializer,
    AirportTimeZoneSerializer,
    AirportListSerializer,
)

COUNTRY_URL = reverse("airport:country-list")
CITY_URL = reverse("airport:city-list")
TIMEZONE_URL = reverse("airport:airporttimezone-list")
AIRPORT_URL = reverse("airport:airport-list")


def sample_country(**params):
    defaults = {
        "name": "Argentina",
    }
    defaults.update(params)
    return Country.objects.create(**defaults)


def sample_time_zone(**params):
    defaults = {
        "name": "America/Argentina/Buenos_Aires",
    }
    defaults.update(params)
    return AirportTimeZone.objects.create(**defaults)


class UnAuthenticatedApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_country_list_and_detail(self):
        response = self.client.get(COUNTRY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        country = sample_country()
        response = self.client.post(COUNTRY_URL + f"{country.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_city_list_and_detail(self):
        response = self.client.get(CITY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        city = City.objects.create(name="Cordoba", country=sample_country())
        response = self.client.post(CITY_URL + f"{city.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_time_zone_list_and_detail(self):
        response = self.client.get(TIMEZONE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        time_zone = sample_time_zone()
        response = self.client.post(TIMEZONE_URL + f"{time_zone.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_airport_list_and_detail(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        airport = Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=City.objects.create(
                name="Cordoba", country=sample_country()
            ),
            time_zone=sample_time_zone(),
        )
        response = self.client.post(AIRPORT_URL + f"{airport.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
        )
        self.client.force_authenticate(user=self.user)

    #  Country
    def test_country_list(self):
        sample_country(name="Spain")
        sample_country()
        sample_country(name="Poland")

        response = self.client.get(COUNTRY_URL)
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        self.assertEqual(serializer.data[0]["name"], "Argentina")
        self.assertEqual(serializer.data[1]["name"], "Poland")
        self.assertEqual(serializer.data[2]["name"], "Spain")

    def test_create_country_forbidden(self):
        payload = {
            "name": "Peru"
        }
        response = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_country_retrieve(self):
        country = sample_country()

        response = self.client.get(COUNTRY_URL + f"{country.id}/")
        serializer = CountrySerializer(country)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_country_update_forbidden(self):
        country = sample_country()
        url = COUNTRY_URL + f"{country.id}/"
        data = {"name": "New Country Name"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #  City
    def test_city_list(self):
        City.objects.create(name="Cordoba", country=sample_country())
        City.objects.create(
            name="Madrid", country=sample_country(name="Spain")
        )
        City.objects.create(
            name="Antalya", country=sample_country(name="Turkey")
        )

        response = self.client.get(CITY_URL)
        cities = City.objects.all()
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        self.assertEqual(serializer.data[0]["name"], "Antalya")
        self.assertEqual(serializer.data[1]["name"], "Cordoba")
        self.assertEqual(serializer.data[2]["name"], "Madrid")

        self.assertEqual(serializer.data[0]["country"], "Turkey")

    def test_create_city_forbidden(self):
        payload = {
            "name": "Cordoba",
            "country": sample_country()
        }
        response = self.client.post(CITY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_city_retrieve(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        response = self.client.get(CITY_URL + f"{city.id}/")
        serializer = CitySerializer(city)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(serializer.data["country"], 1)

    def test_city_update_forbidden(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        url = CITY_URL + f"{city.id}/"
        data = {"name": "New City Name"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #  AirportTimeZone
    def test_time_zone_list(self):
        sample_time_zone()
        sample_time_zone(name="Spain/Madrid")

        response = self.client.get(TIMEZONE_URL)
        time_zones = AirportTimeZone.objects.all()
        serializer = AirportTimeZoneSerializer(time_zones, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_time_zone_forbidden(self):
        payload = {
            "name": "Spain/Madrid"
        }
        response = self.client.post(TIMEZONE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_time_zone_retrieve(self):
        time_zone = sample_time_zone()

        response = self.client.get(TIMEZONE_URL + f"{time_zone.id}/")
        serializer = AirportTimeZoneSerializer(time_zone)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_time_zone_update_forbidden(self):
        time_zone = sample_time_zone()
        url = TIMEZONE_URL + f"{time_zone.id}/"
        data = {"name": "New Time Zone"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #  Airport
    def test_airport_list(self):
        Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=City.objects.create(
                name="Cordoba", country=sample_country()
            ),
            time_zone=sample_time_zone(),
        )
        Airport.objects.create(
            name="El Prat Airport",
            cod_iata="BCL",
            closest_big_city=City.objects.create(
                name="Barcelona", country=sample_country(name="Spain")
            ),
            time_zone=sample_time_zone(name="Spain/Madrid")
        )

        response = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        self.assertEqual(serializer.data[0]["closest_big_city"], "Cordoba")
        self.assertEqual(
            serializer.data[0]["time_zone"], "America/Argentina/Buenos_Aires"
        )
        self.assertEqual(serializer.data[0]["country"], "Argentina")

    def test_create_airport_forbidden(self):
        payload = {
            "name": "Cordoba Airport",
            "cod_iata": "COR",
        }
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airport_retrieve(self):
        airport = Airport.objects.create(
            name="El Prat Airport",
            cod_iata="BCL",
            closest_big_city=City.objects.create(
                name="Barcelona", country=sample_country(name="Spain")
            ),
            time_zone=sample_time_zone(name="Spain/Madrid")
        )
        response = self.client.get(AIRPORT_URL + f"{airport.id}/")
        serializer = AirportListSerializer(airport)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_update_forbidden(self):
        airport = Airport.objects.create(
            name="El Prat Airport",
            cod_iata="BCL",
            closest_big_city=City.objects.create(
                name="Barcelona", country=sample_country(name="Spain")
            ),
            time_zone=sample_time_zone(name="Spain/Madrid")
        )
        url = AIRPORT_URL + f"{airport.id}/"
        data = {"name": "New Airport"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="admin12345",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_country(self):
        payload = {
            "name": "Spain",
        }
        response = self.client.post(COUNTRY_URL, payload)

        country = Country.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(country, "name"))

    def test_delete_country_forbidden(self):
        country = sample_country()
        url = COUNTRY_URL + f"{country.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_city(self):
        payload = {
            "name": "Cordoba",
            "country": sample_country().id,
        }
        response = self.client.post(CITY_URL, payload)
        city = City.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(city, "name"))
        self.assertEqual(payload["country"], getattr(city, "country_id"))

    def test_delete_city_forbidden(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        url = CITY_URL + f"{city.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_time_zone(self):
        payload = {
            "name": "Spain/Madrid",
        }
        response = self.client.post(TIMEZONE_URL, payload)

        time_zone = AirportTimeZone.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(time_zone, "name"))

    def test_delete_time_zone_forbidden(self):
        time_zone = sample_time_zone()
        url = TIMEZONE_URL + f"{time_zone.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_airport(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        time_zone = sample_time_zone()
        payload = {
            "name": "Cordoba Airport",
            "cod_iata": "COR",
            "closest_big_city": city.id,
            "time_zone": time_zone.id,
        }
        response = self.client.post(AIRPORT_URL, payload)

        airport = Airport.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(airport, "name"))
        self.assertEqual(payload["cod_iata"], getattr(airport, "cod_iata"))
        self.assertEqual(
            payload["closest_big_city"],
            getattr(airport, "closest_big_city_id")
        )
        self.assertEqual(
            payload["time_zone"], getattr(airport, "time_zone_id")
        )

        # cod_iata  - unique
        payload["name"] = "Airport Cordoba 2"
        payload["cod_iata"] = "COR"
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # validation cod_iata 3 upper chars
        payload["cod_iata"] = "CAAA"
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_airport_forbidden(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        time_zone = sample_time_zone()
        airport = Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=city,
            time_zone=time_zone,
        )
        url = AIRPORT_URL + f"{airport.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
