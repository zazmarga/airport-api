import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import (
    AirplaneType,
    AirlineCompany,
    Country,
    Facility,
    Airplane
)
from airport.serializers import (
    AirlineCompanyListSerializer,
    AirplaneTypeSerializer,
    FacilitySerializer,
    AirplaneListSerializer
)

TYPE_URL = reverse("airport:airplanetype-list")
COMPANY_URL = reverse("airport:airlinecompany-list")
FACILITY_URL = reverse("airport:facility-list")
AIRPLANE_URL = reverse("airport:airplane-list")


def sample_type(**params):
    defaults = {
        "name": "Passenger Jets",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_facility(**params):
    defaults = {
        "name": "Wi-Fi",
    }
    defaults.update(params)
    return Facility.objects.create(**defaults)


class UnAuthenticatedApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_airplane_type_list_and_detail(self):
        response = self.client.get(TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        airplane_type = sample_type()
        response = self.client.post(TYPE_URL + f"{airplane_type.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_airline_company_list_and_detail(self):
        response = self.client.get(COMPANY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        company = AirlineCompany.objects.create(
            name="Iberia",
            registration_country=Country.objects.create(name="Spain"),
        )
        response = self.client.post(COMPANY_URL + f"{company.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_facility_list_and_detail(self):
        response = self.client.get(FACILITY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        facility = Facility.objects.create(name="Wi-Fi")
        response = self.client.post(FACILITY_URL + f"{facility.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_airplane_list_and_detail(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        company = AirlineCompany.objects.create(
            name="Iberia",
            registration_country=Country.objects.create(name="Spain"),
        )
        airplane = Airplane.objects.create(
            name="AJ-380",
            rows=24,
            seats_in_row=6,
            airplane_type=sample_type(),
            airline_company=company,
        )
        response = self.client.post(AIRPLANE_URL + f"{airplane.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
        )
        self.client.force_authenticate(user=self.user)

    # AirplaneType
    def test_airline_type_list(self):
        sample_type()
        sample_type(name="Narrow-Body Aircraft")

        response = self.client.get(TYPE_URL)
        types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        self.assertEqual(serializer.data[0]["name"], "Narrow-Body Aircraft")
        self.assertEqual(serializer.data[1]["name"], "Passenger Jets")

    def test_create_airline_type_forbidden(self):
        payload = {
            "name": "Narrow-Body Aircraft"
        }
        response = self.client.post(TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airline_type_retrieve(self):
        airline_type = sample_type()

        response = self.client.get(TYPE_URL + f"{airline_type.id}/")
        serializer = AirplaneTypeSerializer(airline_type)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airline_type_update_forbidden(self):
        airline_type = sample_type()
        url = TYPE_URL + f"{airline_type.id}/"
        data = {"name": "New AirlineType Name"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Facility
    def test_facility_list(self):
        sample_facility()
        sample_facility(name="Food service")

        response = self.client.get(FACILITY_URL)
        facilities = Facility.objects.all()
        serializer = FacilitySerializer(facilities, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

        self.assertEqual(serializer.data[0]["name"], "Food service")
        self.assertEqual(serializer.data[1]["name"], "Wi-Fi")

    def test_create_facility_forbidden(self):
        payload = {
            "name": "Food service"
        }
        response = self.client.post(FACILITY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_facility_retrieve(self):
        facility = sample_facility()

        response = self.client.get(FACILITY_URL + f"{facility.id}/")
        serializer = AirplaneTypeSerializer(facility)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_facility_update_forbidden(self):
        facility = sample_type()
        url = FACILITY_URL + f"{facility.id}/"
        data = {"name": "New Facility Name"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # AirlineCompany
    def test_airline_company_list(self):
        AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        AirlineCompany.objects.create(
            name="Aerolineas Argentinas",
            registration_country=Country.objects.create(name="Argentina"),
        )

        response = self.client.get(COMPANY_URL)
        companies = AirlineCompany.objects.all()
        serializer = AirlineCompanyListSerializer(companies, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertIn("logo", serializer.data[0].keys())

        self.assertEqual(serializer.data[0]["name"], "Aerolineas Argentinas")
        self.assertEqual(serializer.data[1]["name"], "Iberica")

    def test_create_airline_company_forbidden(self):
        payload = {
            "name": "Iberica",
            "registration_country": Country.objects.create(name="Spain"),
        }
        response = self.client.post(COMPANY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airline_company_retrieve(self):
        company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        response = self.client.get(COMPANY_URL + f"{company.id}/")
        serializer = AirlineCompanyListSerializer(company)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("logo", serializer.data.keys())

    def test_airline_company_update_forbidden(self):
        company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        url = COMPANY_URL + f"{company.id}/"
        data = {"name": "New AirlineCompany Name"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = COMPANY_URL + f"{company.id}/upload-logo/"
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #  Airplane
    def test_airplane_list_and_retrieve(self):
        airplane_type = sample_type()
        airline_company = AirlineCompany.objects.create(
            name="Iberica",
            registration_country=Country.objects.create(name="Spain"),
        )
        Airplane.objects.create(
            name="IB-007",
            rows=24,
            seats_in_row=6,
            airplane_type=airplane_type,
            airline_company=airline_company,
        )
        airplane2 = Airplane.objects.create(
            name="IB-001",
            rows=28,
            seats_in_row=8,
            airplane_type=airplane_type,
            airline_company=airline_company,
        )
        response = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertIn("capacity", serializer.data[0].keys())
        self.assertEqual(serializer.data[0]["capacity"], 144)

        facility1 = sample_facility()
        facility2 = sample_facility(name="Food service")
        airplane2.facilities.add(facility1, facility2)

        response = self.client.get(AIRPLANE_URL)
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(serializer.data, response.data["results"])
        self.assertEqual(
            response.data["results"][1]["facilities"],
            serializer.data[1]["facilities"]
        )

        response = self.client.get(AIRPLANE_URL + f"{airplane2.id}/")
        serializer = AirplaneListSerializer(airplane2, many=False)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "IB-007",
            "rows": 24,
            "seats_in_row": 6,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_airplane_update_forbidden(self):
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
        data = {"name": "New Airplane Name"}
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
