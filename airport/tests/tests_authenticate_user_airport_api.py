from datetime import datetime

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model

from airport.models import (
    Airport,
    City,
    Route,
    AirlineCompany,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
    Role,
    Country,
    Facility,
    AirplaneType,
    AirportTimeZone
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
    ORDER_URL,
)
from ..serializers import (
    CountrySerializer,
    CityListSerializer,
    CitySerializer,
    AirportTimeZoneSerializer,
    AirportListSerializer,
    AirplaneTypeSerializer,
    FacilitySerializer,
    AirlineCompanyListSerializer,
    AirplaneListSerializer,
    RoleSerializer,
    CrewListSerializer,
    CrewSerializer,
    RouteListSerializer,
    FlightListSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
        )
        self.client.force_authenticate(user=self.user)

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
        self.role = sample_role()
        self.crew = Crew.objects.create(
            first_name="Anna", last_name="Dzen", role=self.role
        )
        self.flight = Flight.objects.create(
            name="AB - 007",
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2025, 1, 7, 20, 55, 0),
            arrival_time=datetime(2025, 1, 8, 19, 45, 0),
            is_completed=False,
        )
        self.order = Order.objects.create(
            created_at=datetime.now(),
            user=self.user
        )

    #  create
    def create_instance_forbidden(self, url, data):
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_country_forbidden(self):
        payload = {
            "name": "Peru"
        }
        self.create_instance_forbidden(COUNTRY_URL, payload)

    def test_create_city_forbidden(self):
        payload = {
            "name": "Cordoba",
            "country": self.country
        }
        self.create_instance_forbidden(CITY_URL, payload)

    def test_create_time_zone_forbidden(self):
        payload = {
            "name": "Spain/Madrid"
        }
        self.create_instance_forbidden(TIMEZONE_URL, payload)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "Cordoba Airport",
            "cod_iata": "COR",
        }
        self.create_instance_forbidden(AIRPORT_URL, payload)

    def test_create_airline_type_forbidden(self):
        payload = {
            "name": "Narrow-Body Aircraft"
        }
        self.create_instance_forbidden(TYPE_URL, payload)

    def test_create_facility_forbidden(self):
        payload = {
            "name": "Food service"
        }
        self.create_instance_forbidden(FACILITY_URL, payload)

    def test_create_airline_company_forbidden(self):
        payload = {
            "name": "Iberica",
            "registration_country": Country.objects.get_or_create(
                name="Spain"
            )[0],
        }
        self.create_instance_forbidden(COMPANY_URL, payload)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "IB-007",
            "rows": 24,
            "seats_in_row": 6,
        }
        self.create_instance_forbidden(AIRPLANE_URL, payload)

    def test_create_role_forbidden(self):
        payload = {
            "name": "Co-pilot"
        }
        self.create_instance_forbidden(ROLE_URL, payload)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Cecilia",
            "last_name": "Aguera",
        }
        self.create_instance_forbidden(CREW_URL, payload)

    def test_create_route_forbidden(self):
        payload = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
        }
        self.create_instance_forbidden(ROUTE_URL, payload)

    def test_create_flight_forbidden(self):
        payload = {
            "name": "AB - 207",
            "route": self.route,
            "airplane": self.airplane,
        }
        self.create_instance_forbidden(FLIGHT_URL, payload)

    #  list & retrieve
    def list_of_instances(
            self, url, list_instances,
            serializer_class,
            ordering: bool = False,
            attrb: str = None
    ):
        response = self.client.get(url)
        serializer = serializer_class(list_instances, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        if ordering:
            prev = serializer.data[0]
            for each in serializer.data[1:]:
                self.assertLessEqual(prev[attrb], each[attrb])
                prev = each

    def retrieve_instance(self, url, instance, serializer_class):
        response = self.client.get(url + f"{instance.id}/")
        serializer = serializer_class(instance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_country_list_and_retrieve(self):
        country = sample_country(name="Poland")
        countries = Country.objects.all()

        self.list_of_instances(
            COUNTRY_URL, countries, CountrySerializer, True, "name"
        )
        self.retrieve_instance(
            COUNTRY_URL, country, CountrySerializer
        )

    def test_city_list_and_retrieve(self):
        city = City.objects.create(
            name="Antalya",
            country=Country.objects.get_or_create(name="Turkey")[0]
        )
        cities = City.objects.all()

        self.list_of_instances(
            CITY_URL, cities, CityListSerializer, True, "name"
        )
        self.retrieve_instance(
            CITY_URL, city, CitySerializer
        )

    def test_time_zone_list_and_retrieve(self):
        time_zone = sample_time_zone(name="Spain/Madrid")
        time_zones = AirportTimeZone.objects.all()

        self.list_of_instances(
            TIMEZONE_URL, time_zones, AirportTimeZoneSerializer, False
        )
        self.retrieve_instance(
            TIMEZONE_URL, time_zone, AirportTimeZoneSerializer
        )

    def test_airport_list_and_retrieve(self):
        airport = Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=City.objects.get_or_create(
                name="Cordoba", country=self.country
            )[0],
            time_zone=sample_time_zone(),
        )
        airports = Airport.objects.all()

        self.list_of_instances(
            AIRPORT_URL, airports, AirportListSerializer, False
        )
        self.retrieve_instance(
            AIRPORT_URL, airport, AirportListSerializer
        )

    def test_airline_type_list_and_retrieve(self):
        airline_type = sample_type(name="Narrow-Body Aircraft")
        airline_types = AirplaneType.objects.all()

        self.list_of_instances(
            TYPE_URL, airline_types, AirplaneTypeSerializer, True, "name"
        )
        self.retrieve_instance(
            TYPE_URL, airline_type, AirplaneTypeSerializer
        )

    def test_facility_list_and_retrieve(self):
        facility = sample_facility(name="Food service")
        facilities = Facility.objects.all()

        self.list_of_instances(
            FACILITY_URL, facilities, FacilitySerializer, True, "name"
        )
        self.retrieve_instance(
            FACILITY_URL, facility, FacilitySerializer
        )

    def test_airline_company_list_and_retrieve(self):
        company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.get_or_create(
                name="Spain"
            )[0],
        )
        companies = AirlineCompany.objects.all()

        self.list_of_instances(
            COMPANY_URL, companies, AirlineCompanyListSerializer, True, "name"
        )
        self.retrieve_instance(
            COMPANY_URL, company, AirlineCompanyListSerializer
        )

    def test_airplane_list_and_retrieve_with_capacity_and_facilities(self):
        airline_company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.get_or_create(
                name="Spain"
            )[0],
        )
        airplane = Airplane.objects.create(
            name="AB-320",
            rows=24,
            seats_in_row=6,
            airplane_type=self.airplane_type,
            airline_company=airline_company,
        )
        airplanes = Airplane.objects.all()

        self.list_of_instances(
            AIRPLANE_URL, airplanes, AirplaneListSerializer, False,
        )
        self.retrieve_instance(
            AIRPLANE_URL, airplane, AirplaneListSerializer
        )

        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertIn("capacity", serializer.data[0].keys())
        self.assertEqual(serializer.data[0]["capacity"], 144)

        facility1 = self.facility
        facility2 = sample_facility(name="Food service")
        airplane.facilities.add(facility1, facility2)

        response = self.client.get(AIRPLANE_URL)
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(serializer.data, response.data["results"])
        self.assertEqual(
            response.data["results"][1]["facilities"],
            serializer.data[1]["facilities"]
        )

    def test_role_list_and_retrieve(self):
        role = sample_role(name="Co-pilot")
        roles = Role.objects.all()

        self.list_of_instances(
            ROLE_URL, roles, RoleSerializer, False,
        )
        self.retrieve_instance(
            ROLE_URL, role, RoleSerializer
        )

    def test_crew_list_and_retrieve(self):
        crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
            role=sample_role(name="Co-pilot"),
        )
        crews = Crew.objects.all()

        self.list_of_instances(
            CREW_URL, crews, CrewListSerializer, False,
        )
        self.retrieve_instance(
            CREW_URL, crew, CrewSerializer
        )

    def test_route_list_and_retrieve(self):
        airport = Airport.objects.create(
            name="Cordoba Airport",
            cod_iata="COR",
            closest_big_city=City.objects.create(
                name="Cordoba",
                country=self.country
            ),
            time_zone=self.time_zone,
        )
        route = Route.objects.create(
            source=self.airport1, destination=airport, distance=620
        )
        routes = Route.objects.all()
        self.list_of_instances(
            ROUTE_URL, routes, RouteListSerializer, False,
        )
        self.retrieve_instance(
            ROUTE_URL, route, RouteListSerializer
        )

    def test_flight_list_and_retrieve(self):
        crew1 = self.crew
        crew2 = Crew.objects.create(
            first_name="Mark",
            last_name="Colin",
            role=sample_role(name="Capitan"),
        )
        flight = Flight.objects.create(
            name="AB - 777",
            route=self.route,
            airplane=self.airplane,
            departure_time=datetime(2025, 1, 4, 20, 00, 0),
            arrival_time=datetime(2025, 1, 5, 20, 00, 0),
            is_completed=False,
        )

        flight.crew_members.add(crew1, crew2)
        flights = Flight.objects.all()
        self.list_of_instances(
            FLIGHT_URL, flights, FlightListSerializer, True, "departure_time"
        )
        self.retrieve_instance(
            FLIGHT_URL, flight, FlightListSerializer
        )

        flight.is_completed = True
        flight.save()
        flights = Flight.objects.all()
        self.list_of_instances(
            FLIGHT_URL, flights, FlightListSerializer, True, "is_completed"
        )

        serializer = FlightListSerializer(flight)
        self.assertEqual(serializer.data["duration"], "20h 21m")
        self.assertEqual(serializer.data["crew_members"][0], crew1.full_name)

    #  update forbidden
    def update_forbidden(self, url, instance_id, data):
        url = url + f"{instance_id}/"
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_country_update_forbidden(self):
        country = self.country
        data = {"name": "New Country Name"}
        self.update_forbidden(COUNTRY_URL, country.id, data)

    def test_city_update_forbidden(self):
        city = City.objects.create(name="Cordoba", country=self.country)
        data = {"name": "New City Name"}
        self.update_forbidden(CITY_URL, city.id, data)

    def test_time_zone_update_forbidden(self):
        time_zone = self.time_zone
        data = {"name": "New Time Zone"}
        self.update_forbidden(TIMEZONE_URL, time_zone.id, data)

    def test_airport_update_forbidden(self):
        airport = self.airport1
        data = {"name": "New Airport"}
        self.update_forbidden(AIRPORT_URL, airport.id, data)

    def test_airline_type_update_forbidden(self):
        airplane_type = self.airplane_type
        data = {"name": "New Airplane Type"}
        self.update_forbidden(TYPE_URL, airplane_type.id, data)

    def test_facility_update_forbidden(self):
        facility = self.facility
        data = {"name": "New Facility Name"}
        self.update_forbidden(FACILITY_URL, facility.id, data)

    def test_airline_company_update_forbidden(self):
        company = self.airline_company
        data = {"name": "New AirlineCompany Name"}
        self.update_forbidden(COMPANY_URL, company.id, data)

    def test_airplane_update_forbidden(self):
        airplane = self.airplane
        data = {"name": "New Airplane Name"}
        self.update_forbidden(AIRPLANE_URL, airplane.id, data)

    def test_role_update_forbidden(self):
        role = sample_role(name="Co-pilot")
        data = {"name": "New Role Name"}
        self.update_forbidden(ROLE_URL, role.id, data)

    def test_crew_update_forbidden(self):
        crew = self.crew
        data = {"first_name": "New First Name"}
        self.update_forbidden(CREW_URL, crew.id, data)

    def test_route_update_forbidden(self):
        route = self.route
        data = {"distance": 5000}
        self.update_forbidden(ROUTE_URL, route.id, data)

    def test_flight_update_forbidden(self):
        flight = self.flight
        data = {"name": "New Flight Name"}
        self.update_forbidden(FLIGHT_URL, flight.id, data)

    #  tests order
    def test_order_create(self):
        ticket1 = {
            "row": 2,
            "seat": "A",
            "flight": self.flight.id,
        }
        ticket2 = {
            "row": 2,
            "seat": "B",
            "flight": self.flight.id,
        }
        payload = {
            "created_at": datetime.now(),
            "user": self.user.id,
            "tickets": [ticket1, ticket2],
        }

        response = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("id", response.data)
        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.tickets.count(), 2)

    def test_order_list(self):
        client = APIClient()
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="other12345",
        )
        client.force_authenticate(user=other_user)
        ticket = {
            "row": 10,
            "seat": "E",
            "flight": self.flight.id,
        }
        payload = {
            "created_at": datetime.now(),
            "user": other_user.id,
            "tickets": [ticket],
        }
        response = client.post(ORDER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        client.logout()

        orders = Order.objects.filter(user=self.user)
        response = self.client.get(ORDER_URL)
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_order_retrieve(self):
        self.order.tickets.add(
            Ticket.objects.create(
                row=10,
                seat="E",
                flight=self.flight,
                order=self.order
            )
        )
        response = self.client.get(ORDER_URL + f"{self.order.id}/")
        serializer = OrderRetrieveSerializer(self.order)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        self.assertIn("tickets", response.data)
        self.assertIn("flight", response.data["tickets"][0])

    def test_order_update(self):
        ticket1 = {
            "row": 11,
            "seat": "A",
            "flight": self.flight.id,
        }
        payload = {
            "created_at": datetime.now(),
            "user": self.user.id,
            "tickets": [ticket1],
        }
        response = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(pk=response.data["id"])

        url = ORDER_URL + f"{order.id}/"

        ticket_new = Ticket.objects.create(
            row=11,
            seat="B",
            flight=self.flight,
            order=order
        )
        order.tickets.add(ticket_new)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["tickets"]), 2)

    def test_delete_order(self):
        order = self.order
        url = ORDER_URL + f"{order.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
