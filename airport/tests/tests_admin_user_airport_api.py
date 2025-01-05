import os
import tempfile
from datetime import datetime

from PIL import Image
from django.test import TestCase
from rest_framework import status

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from airport.models import (
    Country,
    City,
    AirportTimeZone,
    Airport,
    Facility,
    AirplaneType,
    AirlineCompany,
    Airplane,
    Role,
    Crew,
    Route,
    Flight
)
from airport.tests.urls_and_sample_functions import (
    COUNTRY_URL, sample_country,
    CITY_URL,
    TIMEZONE_URL, sample_time_zone,
    AIRPORT_URL,
    FACILITY_URL, sample_facility,
    TYPE_URL, sample_type,
    COMPANY_URL,
    AIRPLANE_URL,
    ROLE_URL, sample_role,
    CREW_URL,
    ROUTE_URL,
    FLIGHT_URL,
)


def sample_flight():
    airport1 = Airport.objects.create(
        name="Eseiza",
        cod_iata="EZE",
        closest_big_city=City.objects.get_or_create(
            name="Buenos Aires",
            country=Country.objects.get_or_create(name="Argentina")[0]
        )[0],
        time_zone=sample_time_zone(),
    )
    airport2 = Airport.objects.create(
        name="El Prat",
        cod_iata="BCN",
        closest_big_city=City.objects.get_or_create(
            name="Barcelona",
            country=Country.objects.get_or_create(name="Spain")[0]
        )[0],
        time_zone=sample_time_zone(name="Europe/Madrid"),
    )
    airline_company = AirlineCompany.objects.create(
        name="Aerolineas Argentinas",
        registration_country=Country.objects.get_or_create(name="Argentina")[0]
    )
    airplane = Airplane.objects.create(
        name="Boeing 747",
        rows=24,
        seats_in_row=6,
        airplane_type=sample_type(),
        airline_company=airline_company,
    )
    crew = Crew.objects.create(
        first_name="Anna", last_name="Dzen", role=sample_role(),
    )
    flight = Flight.objects.create(
        name="AB - 777",
        route=Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=10560,
        ),
        airplane=airplane,
        departure_time=datetime(2025, 1, 3, 20, 55, 0, tzinfo=None),
        arrival_time=datetime(2025, 1, 4, 20, 55, 0, tzinfo=None),
    )
    flight.crew_members.add(crew)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="admin12345",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def create_instance(self, url, payload, class_instance):
        response = self.client.post(url, payload)

        instance = class_instance.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            if hasattr(instance, f"{key}_id"):
                self.assertEqual(payload[key], getattr(instance, f"{key}_id"))
            else:
                self.assertEqual(payload[key], getattr(instance, key))

    def test_create_country(self):
        payload = {
            "name": "Spain",
        }
        self.create_instance(COUNTRY_URL, payload, Country)

    def test_create_city(self):
        payload = {
            "name": "Cordoba",
            "country": sample_country().id,
        }
        self.create_instance(CITY_URL, payload, City)

    def test_create_time_zone(self):
        payload = {
            "name": "Spain/Madrid",
        }
        self.create_instance(TIMEZONE_URL, payload, AirportTimeZone)

    def test_create_airport(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        time_zone = sample_time_zone()
        payload = {
            "name": "Cordoba Airport",
            "cod_iata": "COR",
            "closest_big_city": city.id,
            "time_zone": time_zone.id,
        }
        self.create_instance(AIRPORT_URL, payload, Airport)

        # cod_iata  - unique
        payload["name"] = "Airport Cordoba 2"
        payload["cod_iata"] = "COR"
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # validation cod_iata 3 upper chars
        payload["cod_iata"] = "CAAA"
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_facility(self):
        payload = {
            "name": "Wi-Fi",
        }
        self.create_instance(FACILITY_URL, payload, Facility)

    def test_create_airplane_type(self):
        payload = {
            "name": "Passenger Jets",
        }
        self.create_instance(TYPE_URL, payload, AirplaneType)

    def test_create_airline_company(self):
        payload = {
            "name": "Iberica",
            "registration_country": Country.objects.create(name="Spain").id,
        }
        self.create_instance(COMPANY_URL, payload, AirlineCompany)

    def test_upload_logo_of_airline_company_allowed(self):
        company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        url = COMPANY_URL + f"{company.id}/upload-logo/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_airplane(self):
        airplane_type = sample_type()
        airline_company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        payload = {
            "name": "IB-007",
            "rows": 24,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
            "airline_company": airline_company.id,
        }
        self.create_instance(AIRPLANE_URL, payload, Airplane)

    def test_create_role(self):
        payload = {
            "name": "Capitan",
        }
        self.create_instance(ROLE_URL, payload, Role)

    def test_create_crew(self):
        payload = {
            "first_name": "Anna",
            "last_name": "Dzen",
            "role": sample_role().id,
        }
        self.create_instance(CREW_URL, payload, Crew)

    def test_create_route(self):
        airport1 = Airport.objects.create(
            name="Eseiza",
            cod_iata="EZE",
            closest_big_city=City.objects.get_or_create(
                name="Buenos Aires",
                country=Country.objects.get_or_create(name="Argentina")[0]
            )[0],
            time_zone=sample_time_zone(),
        )
        airport2 = Airport.objects.create(
            name="El Prat",
            cod_iata="BCN",
            closest_big_city=City.objects.get_or_create(
                name="Barcelona",
                country=Country.objects.get_or_create(name="Spain")[0]
            )[0],
            time_zone=sample_time_zone(name="Europe/Madrid"),
        )
        payload = {
            "source": airport1.id,
            "destination": airport2.id,
            "distance": 10560,
        }
        self.create_instance(ROUTE_URL, payload, Route)

    def test_create_flight(self):
        airport1 = Airport.objects.create(
            name="Eseiza",
            cod_iata="EZE",
            closest_big_city=City.objects.get_or_create(
                name="Buenos Aires",
                country=Country.objects.get_or_create(name="Argentina")[0]
            )[0],
            time_zone=sample_time_zone(),
        )
        airport2 = Airport.objects.create(
            name="El Prat",
            cod_iata="BCN",
            closest_big_city=City.objects.get_or_create(
                name="Barcelona",
                country=Country.objects.get_or_create(name="Spain")[0]
            )[0],
            time_zone=sample_time_zone(name="Europe/Madrid"),
        )
        airline_company = AirlineCompany.objects.create(
            name="Aerolineas Argentinas",
            registration_country=Country.objects.get_or_create(
                name="Argentina"
            )[0]
        )
        airplane = Airplane.objects.create(
            name="Boeing 747",
            rows=24,
            seats_in_row=6,
            airplane_type=sample_type(),
            airline_company=airline_company,
        )
        crew = Crew.objects.create(
            first_name="Anna", last_name="Dzen", role=sample_role(),
        )
        payload = {
            "name": "AB - 207",
            "route": Route.objects.create(
                source=airport1,
                destination=airport2,
                distance=10560,
            ).id,
            "airplane": airplane.id,
            "departure_time": datetime(2025, 1, 3, 20, 55, 0, tzinfo=None),
            "arrival_time": datetime(2025, 1, 4, 20, 55, 0, tzinfo=None),
            "crew_members": [crew.id],
        }

        response = self.client.post(FLIGHT_URL, payload)
        self.flight = Flight.objects.get(pk=response.data["id"])
        flight = self.flight

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            if hasattr(flight, f"{key}_id"):
                self.assertEqual(payload[key], getattr(flight, f"{key}_id"))

        self.assertEqual(payload["name"], getattr(flight, "name"))

        flight.departure_time = flight.departure_time.replace(tzinfo=None)
        payload["departure_time"] = payload["departure_time"].replace(
            tzinfo=None
        )
        self.assertEqual(
            payload["departure_time"], getattr(flight, "departure_time")
        )

        flight.arrival_time = flight.arrival_time.replace(tzinfo=None)
        payload["arrival_time"] = payload["arrival_time"].replace(tzinfo=None)
        self.assertEqual(
            payload["arrival_time"], getattr(flight, "arrival_time")
        )

        crews = flight.crew_members.all()
        self.assertEqual(crews.count(), 1)
        self.assertIn(crew, crews)

    #  delete forbidden
    def delete_instance_forbidden(self, url, instance):
        response = self.client.delete(url + f"{instance.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_country_forbidden(self):
        country = sample_country()
        self.delete_instance_forbidden(COUNTRY_URL, country)

    def test_delete_city_forbidden(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        self.delete_instance_forbidden(CITY_URL, city)

    def test_delete_time_zone_forbidden(self):
        time_zone = sample_time_zone()
        self.delete_instance_forbidden(TIMEZONE_URL, time_zone)

    def test_delete_airport_forbidden(self):
        city = City.objects.create(name="Cordoba", country=sample_country())
        time_zone = sample_time_zone()
        airport = Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=city,
            time_zone=time_zone,
        )
        self.delete_instance_forbidden(AIRPORT_URL, airport)

    def test_delete_facility_forbidden(self):
        facility = sample_facility()
        self.delete_instance_forbidden(FACILITY_URL, facility)

    def test_delete_airplane_type_forbidden(self):
        airplane_type = sample_type()
        self.delete_instance_forbidden(TYPE_URL, airplane_type)

    def test_delete_airline_company_forbidden(self):
        company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        self.delete_instance_forbidden(COMPANY_URL, company)

    def test_delete_airplane_forbidden(self):
        airplane_type = sample_type()
        airline_company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        airplane = Airplane.objects.create(
            name="IB-007",
            rows=24,
            seats_in_row=6,
            airplane_type=airplane_type,
            airline_company=airline_company,
        )
        self.delete_instance_forbidden(AIRPLANE_URL, airplane)

    def test_delete_role_forbidden(self):
        role = sample_role(name="Co-pilot")
        self.delete_instance_forbidden(ROLE_URL, role)

    def test_delete_crew_forbidden(self):
        crew = Crew.objects.create(
            first_name="Anna", last_name="Dzen", role=sample_role(),
        )
        self.delete_instance_forbidden(CREW_URL, crew)

    def test_delete_route_forbidden(self):
        airport1 = Airport.objects.create(
            name="Eseiza",
            cod_iata="EZE",
            closest_big_city=City.objects.get_or_create(
                name="Buenos Aires",
                country=Country.objects.get_or_create(name="Argentina")[0]
            )[0],
            time_zone=sample_time_zone(),
        )
        airport2 = Airport.objects.create(
            name="El Prat",
            cod_iata="BCN",
            closest_big_city=City.objects.get_or_create(
                name="Barcelona",
                country=Country.objects.get_or_create(name="Spain")[0]
            )[0],
            time_zone=sample_time_zone(name="Europe/Madrid"),
        )
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
            distance=10560,
        )
        self.delete_instance_forbidden(ROUTE_URL, route)

    def test_delete_flight_forbidden(self):
        flight, _ = Flight.objects.get_or_create(sample_flight())
        self.delete_instance_forbidden(FLIGHT_URL, flight)


class LogoCompanyUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="admin12345",
        )
        self.client.force_authenticate(self.user)

        self.airline_company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )

    def tearDown(self):
        self.airline_company.logo.delete()

    def test_upload_logo_to_aitline_company(self):
        """Test uploading a logo to airline_company"""
        url = COMPANY_URL + f"{self.airline_company.id}/upload-logo/"
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"logo": ntf}, format="multipart")
        self.airline_company.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("logo", res.data)
        self.assertTrue(os.path.exists(self.airline_company.logo.path))

    def test_upload_logo_bad_request(self):
        """Test uploading an invalid logo"""
        url = COMPANY_URL + f"{self.airline_company.id}/upload-logo/"
        res = self.client.post(url, {"logo": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_logo_to_airline_company_list(self):
        url = COMPANY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Test Name",
                    "registration_country": [1],
                    "logo": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airline_company = AirlineCompany.objects.get(name="Test Name")
        self.assertFalse(airline_company.logo)

    def test_logo_url_is_shown_on_airline_company_detail(self):
        url = COMPANY_URL + f"{self.airline_company.id}/"
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"logo": ntf}, format="multipart")
        res = self.client.get(url)

        self.assertIn("logo", res.data)

    def test_logo_url_is_shown_on_airline_company_list(self):
        url = COMPANY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"logo": ntf}, format="multipart")
        res = self.client.get(COMPANY_URL)
        self.assertIn("logo", res.data["results"][0].keys())
