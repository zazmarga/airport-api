from django.test import TestCase

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

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



    def test_create_facility(self):
        payload = {
            "name": "Wi-Fi",
        }
        response = self.client.post(FACILITY_URL, payload)

        facility = Facility.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(facility, "name"))

    def test_delete_facility_forbidden(self):
        facility = sample_facility()
        url = FACILITY_URL + f"{facility.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_airplane_type(self):
        payload = {
            "name": "Passenger Jets",
        }
        response = self.client.post(TYPE_URL, payload)

        airplane_type = AirplaneType.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(airplane_type, "name"))

    def test_delete_airplane_type_forbidden(self):
        airplane_type = sample_type()
        url = TYPE_URL + f"{airplane_type.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_airline_company(self):
        payload = {
            "name": "Iberica",
            "registration_country": Country.objects.create(name="Spain").id,
        }
        response = self.client.post(COMPANY_URL, payload)

        company = AirlineCompany.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(company, "name"))
        self.assertEqual(
            payload["registration_country"],
            getattr(company, "registration_country_id")
        )

    def test_delete_airline_company_forbidden(self):
        company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )

        url = COMPANY_URL + f"{company.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        response = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(airplane, "name"))
        self.assertEqual(payload["rows"], getattr(airplane, "rows"))
        self.assertEqual(
            payload["seats_in_row"], getattr(airplane, "seats_in_row")
        )
        self.assertEqual(
            payload["airplane_type"], getattr(airplane, "airplane_type_id")
        )
        self.assertEqual(
            payload["airline_company"], getattr(airplane, "airline_company_id")
        )

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

        url = AIRPLANE_URL + f"{airplane.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



    def test_create_role(self):
        payload = {
            "name": "Capitan",
        }
        response = self.client.post(ROLE_URL, payload)

        role = Role.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(role, "name"))

    def test_delete_role_forbidden(self):
        role = sample_role(name="Co-pilot")
        url = ROLE_URL + f"{role.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_crew(self):
        payload = {
            "first_name": "Anna",
            "last_name": "Dzen",
            "role": sample_role().id,
        }
        response = self.client.post(CREW_URL, payload)

        crew = Crew.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["first_name"], getattr(crew, "first_name"))
        self.assertEqual(payload["role"], getattr(crew, "role_id"))

    def test_delete_crew_forbidden(self):
        crew = self.crew
        url = CREW_URL + f"{crew.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_route(self):
        payload = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 10560,
        }
        response = self.client.post(ROUTE_URL, payload)

        route = Route.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["source"], getattr(route, "source_id"))
        self.assertEqual(payload["destination"], getattr(route, "destination_id"))
        self.assertEqual(payload["distance"], getattr(route, "distance"))

    def test_delete_route_forbidden(self):
        route = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=10560,
        )
        url = ROUTE_URL + f"{route.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_flight(self):
        payload = {
            "name": "AB - 207",
            "route": Route.objects.create(
                source=self.airport1,
                destination=self.airport2,
                distance=10560,
            ).id,
            "airplane": self.airplane.id,
            "departure_time": datetime(2025, 1, 3, 20, 55, 0),
            "arrival_time": datetime(2025, 1, 4, 20, 55, 0),
            "crew_members": [self.crew.id],
        }
        response = self.client.post(FLIGHT_URL, payload)

        flight = Flight.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(flight, "name"))
        self.assertEqual(payload["route"], getattr(flight, "route_id"))
        self.assertEqual(payload["airplane"], getattr(flight, "airplane_id"))
        # self.assertNotEqual(payload["departure_time"], getattr(flight, "departure_time"))
        # self.assertNotEqual(payload["arrival_time"], getattr(flight, "arrival_time"))
        # self.assertEqual([1], getattr(flight, "crew_members"))


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


