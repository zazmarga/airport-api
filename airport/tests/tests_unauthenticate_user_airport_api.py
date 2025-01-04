from datetime import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User
from .urls_and_sample_functions import *

from airport.models import (
    Country,
    City,
    Airport,
    AirlineCompany,
    Airplane,
    Crew,
    Route,
    Flight, Order,
)


class UnAuthenticatedApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.country = sample_country()
        self.time_zone = sample_time_zone()
        self.airport1 = Airport.objects.create(
            name="Eseiza",
            cod_iata="EZE",
            closest_big_city=City.objects.create(
                name="Buenos Aires",
                country=self.country
            ),
            time_zone=self.time_zone,
        )
        self.airport2 = Airport.objects.create(
            name="El Prat",
            cod_iata="BCN",
            closest_big_city=City.objects.create(
                name="Barcelona",
                country=Country.objects.get_or_create(name="Spain")[0]
            ),
            time_zone=sample_time_zone(name="Europe/Madrid"),
        )
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=10560
        )
        self.airline_company = AirlineCompany.objects.create(
            name="Aerolineas Argentinas",
            registration_country=self.country
        )
        self.airplane_type = sample_type()
        self.airplane = Airplane.objects.create(
            name="Boeing 747",
            rows=24,
            seats_in_row=6,
            airplane_type=self.airplane_type,
            airline_company=self.airline_company,
        )
        self.facility = sample_facility()
        self.flight = Flight.objects.create(
            name="AB - 007",
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2025, 1, 7, 20, 55, 0),
            arrival_time=datetime(2025, 1, 8, 19, 45, 0),
            is_completed=False,
        )
        self.role = sample_role()

        self.user = User.objects.create_user(
            email="un_auth_user@test.com",
            password="test_password"
        )
        self.order = Order.objects.create(
            created_at=datetime.now(),
            user=self.user,
        )


    def auth_required_list_and_detail(self, url, instance):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(url + f"{instance.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_country_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=COUNTRY_URL, instance=self.country
        )

    def test_auth_required_for_city_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=CITY_URL,
            instance=City.objects.create(name="Cordoba", country=self.country)
        )

    def test_auth_required_for_time_zone_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=TIMEZONE_URL, instance=self.time_zone
        )

    def test_auth_required_for_airport_list_and_detail(self):
        airport = Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=City.objects.create(
                name="Cordoba", country=self.country
            ),
            time_zone=self.time_zone,
        )
        self.auth_required_list_and_detail(
            url=AIRPORT_URL, instance=airport
        )

    def test_auth_required_for_airplane_type_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=TYPE_URL, instance=self.airplane_type
        )

    def test_auth_required_for_airline_company_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=COMPANY_URL,
            instance=AirlineCompany.objects.create(
                name="Iberia",
                registration_country=Country.objects.get_or_create(name="Spain")[0],
            )
        )

    def test_auth_required_for_facility_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=FACILITY_URL, instance=self.facility
        )

    def test_auth_required_for_airplane_list_and_detail(self):
        airplane = Airplane.objects.create(
            name="AJ-380",
            rows=24,
            seats_in_row=6,
            airplane_type=self.airplane_type,
            airline_company=AirlineCompany.objects.create(
                name="Iberia",
                registration_country=Country.objects.get_or_create(name="Spain")[0],
            )
        )
        self.auth_required_list_and_detail(
            url=AIRPLANE_URL, instance=airplane
        )

    def test_auth_required_for_role_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=ROLE_URL, instance=self.role
        )

    def test_auth_required_for_crew_list_and_detail(self):
        crew = Crew.objects.create(
            first_name="Anna", last_name="Dzen", role=self.role
        )
        self.auth_required_list_and_detail(
            url=CREW_URL, instance=crew
        )

    def test_auth_required_for_route_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=ROUTE_URL, instance=self.route
        )

    def test_auth_required_for_flight_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=FLIGHT_URL, instance=self.flight
        )

    def test_auth_required_for_order_list_and_detail(self):
        self.auth_required_list_and_detail(
            url=ORDER_URL, instance=self.order
        )
